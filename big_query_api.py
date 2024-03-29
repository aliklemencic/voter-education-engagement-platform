"""
API to push data to BigQuery.
"""
import os
import openstates_api
import lcv_scraper
import councilmatic_api
from bs4 import BeautifulSoup
from datetime import datetime
from google.cloud import bigquery


def import_lcv_data(first_create):
    '''
    Scrapes the LCV website and pushes resulting data to BigQuery.
    
    Inputs:
        - first_create (bool): true if table needs to be created
    
    Returns: Nothing
    '''
    if first_create:
        schema = [bigquery.SchemaField('name', "STRING", mode="REQUIRED"),
              bigquery.SchemaField('congress', "STRING", mode="REQUIRED"),
              bigquery.SchemaField('party', "STRING", mode="REQUIRED"),
              bigquery.SchemaField('state', "STRING", mode="REQUIRED"),
              bigquery.SchemaField('district', "STRING"),
              bigquery.SchemaField('lcv_rating', "STRING"),
              bigquery.SchemaField('lcv_link', "STRING")]
        insert_table_to_bigquery(schema, 'sixth-window-364916.issuehub.congress_members')
    lcv_data = lcv_scraper.get_lcv_data()
    schema_fields = ['name', 'congress', 'party', 'state',
        'district', 'lcv_rating', 'lcv_link']
    write_rows_to_bigquery(schema_fields, lcv_data, 'congress_members')


def import_legislation(state, keywords, first_create):
    '''
    Retrieves relevant legislation from Open States and pushes the data to BigQuery.
    
    Inputs:
        - keywords (list of str): keywords to search for
        - first_create (bool): true if table needs to be created
    
    Returns: Nothing
    '''
    if first_create:
        schema = [bigquery.SchemaField('openstates_id', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('identifier', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('title', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('openstates_link', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('state', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('create_date', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('latest_action_date', "STRING"),
            bigquery.SchemaField('latest_action_description', "STRING"),
            bigquery.SchemaField('abstract', "STRING")]
        insert_table_to_bigquery(schema, 'sixth-window-364916.issuehub.bills')
    bills = openstates_api.get_data_for_state_and_topic(state, keywords)
    schema_fields = ['openstates_id', 'identifier', 'title',
        'openstates_link', 'state', 'create_date', 'latest_action_date',
        'latest_action_description', 'abstract']
    bill_data = get_bill_data(bills, state)
    write_rows_to_bigquery(schema_fields, bill_data, 'bills')


def get_local_data(location, keywords, first_create):
    '''
    Retrieves local legislation from Councilmatic and pushes the data to BigQuery.
    
    Inputs:
        - keywords (list of str): keywords to search for
        - first_create (bool): true if table needs to be created
    
    Returns: Nothing
    '''
    if first_create:
        schema = [bigquery.SchemaField('councilmatic_id', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('identifier', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('title', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('jurisdiction', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('updated_date', "STRING", mode="REQUIRED"),
            bigquery.SchemaField('from_org', "STRING", mode="REQUIRED")]
        insert_table_to_bigquery(schema, 'sixth-window-364916.issuehub.local_bills')
    bills = councilmatic_api.get_data_for_location_and_topic(location, keywords)
    schema_fields = ['councilmatic_id', 'identifier', 'title', 
        'jurisdiction', 'updated_date', 'from_org']
    bill_data = get_local_bill_data(bills, location)
    write_rows_to_bigquery(schema_fields, bill_data, 'local_bills')


def get_local_bill_data(bills, location):
    '''
    Converts local bill data to a more usable format.
    
    Inputs:
        - bills (list of dicts) bill information
        - location (str): locality
    
    Returns: (list of dicts) reformated bill data
    '''
    bill_data = []
    for bill in bills:
        current_bill = {}
        current_bill['councilmatic_id'] = bill['id']
        current_bill['identifier'] = bill['identifier']
        current_bill['title'] = bill['title']
        current_bill['updated_date'] = bill['updated_at']
        current_bill['from_org'] = bill['from_organization']['name']
        current_bill['jurisdiction'] = location
        bill_data.append(current_bill)
    return bill_data


def get_bill_data(bills, state):
    '''
    Converts state bill data to a more usable format.
    
    Inputs:
        - bills (list of dicts) bill information
        - state (str): state
    
    Returns: (list of dicts) reformated bill data
    '''
    bill_data = []
    for bill in bills:
        current_bill = {}
        current_bill['openstates_id'] = bill[0]['id']
        current_bill['identifier'] = bill[0]['identifier']
        current_bill['title'] = bill[0]['title']
        current_bill['openstates_link'] = bill[0]['openstates_url']
        current_bill['create_date'] = get_date_string(bill[0]['created_at'])
        current_bill['latest_action_date'] = get_date_string(bill[0]['latest_action_date'])
        current_bill['latest_action_description'] = bill[0]['latest_action_description']
        current_bill['state'] = state

        if bill[0]['abstracts']:
            abstract = bill[0]['abstracts'][0]['abstract']
            if '<' in abstract:
                soup = BeautifulSoup(abstract)
                current_bill['abstract'] = ''
                for p in soup.find_all('p'):
                    if p.text == current_bill['title']:
                        continue
                    if current_bill['abstract']:
                        current_bill['abstract'] += " "
                    current_bill['abstract'] += p.text.strip()
            else:
                current_bill['abstract'] = abstract
        else: 
            current_bill['abstract'] = ''

        bill_data.append(current_bill)

    return bill_data


def get_date_string(full_date):
    '''
    Reformats the date into a usable string.

    Inputs:
        - full_date (str): the given date
    
    Returns: (str) the date in a usable string format
    '''
    date = full_date[:10]
    date_object = datetime.strptime(date, '%Y-%m-%d')
    date_string = date_object.strftime('%B %d, %Y')
    return date_string


def create_dataset_bigquery():
    '''
    Creates a dataset in BigQuery.

    Inputs: None

    Returns: Nothing, but prints the name of the dataset
    '''
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './issuehub_cloud_service_admin.json'
    client = bigquery.Client()
    dataset = bigquery.Dataset('issuehub')
    dataset.location = "US"
    dataset = client.create_dataset(dataset, timeout=30)
    print("Created dataset {}.{}".format(dataset.project, dataset.dataset_id))


def write_rows_to_bigquery(schema_fields, data, table_id):
    """
    Writes rows of data to a BigQuery table.

    Inputs:
        - schema_fields (list of str): schema of the table
        - data (list of dicts): rows of bill data to insert
        - table_id (str): id of the table
    
    Returns: Nothing, but prints when successful
    """
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './issuehub_cloud_service_admin.json'
    client = bigquery.Client()

    table_ref = client.dataset('issuehub').table(table_id) 
    table = client.get_table(table_ref)

    insert_list = []
    for row in data:
        values = []
        for key in schema_fields:
            values.append(row[key])
        insert_list.append(tuple(values))

    errors = client.insert_rows(table, insert_list) 
    if errors != []:
        print(errors)
    print("Data successfully inserted into {}.".format(table_id))


def remove_rows_bigquery(table, condition):
    '''
    Removes rows from a BigQuery table.

    Inputs:
        - table (str): the table to remove rows from
        - condition (str): the condition of rows to remove
    
    Returns: Nothing, but prints when successful
    '''
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './issuehub_cloud_service_admin.json'
    client = bigquery.Client()

    sql = "DELETE FROM " + table + " WHERE " + condition

    query_job = client.query(sql)
    query_job.result()
    print("Rows removed from {} where {}".format(table, condition))


def insert_table_to_bigquery(schema, table_id):
    '''
    Adds a new table to BigQuery.

    Inputs:
        - schema (list of str): the schema of the table
        - table_id (str): the id of the table

    Returns: Nothing, but prints when successful
    '''
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './issuehub_cloud_service_admin.json'
    client = bigquery.Client()

    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)
    print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))

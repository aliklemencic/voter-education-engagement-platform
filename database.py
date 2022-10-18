"""
Creates database and makes API calls to Open States and ProPublica.
"""

import pandas as pd
import sqlite3
import openstates_api


def get_state_data(state, keywords):
    """
    Connects to the Open States API to get data on state bills.
    :param state_names: list of states
    :return: Pandas dataframe of bill data for all input states
    """
    state_bills = openstates_api.gget_data_for_state_and_topic(state, keywords)
    state_bills_df = pd.DataFrame(state_bills)

    return state_bills_df


def create_sql_tables(state_names, keywords, topic):
    """
    Creates an SQL table from the state and national dataframes.
    :param state_names: list of states
    :param api_key: (str) API key to connect to ProPublica
    """
    database_name = topic + 'bill_data.db'
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    for state in state_names:
        state_bills_df = get_state_data(state_names, keywords)
        data_name = state + "_" + topic + "_bills"
        state_bills_df.to_sql(data_name, conn)
    
    c.close()


def run():
    """
    Runs the above functions for Illinois and the US for climate change related bills.
    """
    states = ["Illinois", "US"]
    keywords = ["climate", "environment", "energy"]
    topic = "climate_change"

    create_sql_tables(states, keywords, topic)

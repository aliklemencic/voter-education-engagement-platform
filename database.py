"""
Creates database and makes API calls to Open States and ProPublica.
"""

import pandas as pd
import sqlite3
import openstates_api
from congress import Congress


def get_state_data(state_names):
    """
    Connects to the Open States API to get data on state bills.
    :param state_names: list of states
    :return: Pandas dataframe of bill data for all input states
    """
    state_bills = openstates_api.get_data_for_all_states(state_names)
    state_bills_df = pd.DataFrame(state_bills)

    return state_bills_df


def get_national_data(api_key):
    """
    Connects to the ProPublica API to get national House and Senate bill data.
    :param api_key: (str) API key to connect
    :return: Pandas dataframe of House and Senate bill data
    """
    congress = Congress(api_key)

    house_bills = congress.bills.recent('house', congress=117)
    house_df = pd.DataFrame(house_bills['bills'])

    senate_bills = congress.bills.recent('senate', congress=117)
    senate_df = pd.DataFrame(senate_bills['bills'])

    national_bills_df = pd.concat([house_df, senate_df])
    return national_bills_df


def create_sql_tables(state_names, api_key):
    """
    Creates an SQL table from the state and national dataframes.
    :param state_names: list of states
    :param api_key: (str) API key to connect to ProPublica
    """
    # this is currently not functional
    conn = sqlite3.connect('bill_data.db')
    c = conn.cursor()

    state_bills_df = get_state_data(state_names)
    state_bills_df.to_sql("state_bills", conn)

    national_bills_df = get_national_data(api_key)
    national_bills_df.to_sql("national_bills", conn)


def run():
    """
    Runs the above functions for all 50 states and our ProPublica API key.
    """
    # not currently functional
    state_names = ["Alaska", "Alabama", "Arkansas", "Arizona", "California",
                   "Colorado", "Connecticut", "District of Columbia", "Delaware",
                   "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois",
                   "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts",
                   "Maryland", "Maine", "Michigan", "Minnesota", "Missouri",
                   "Mississippi", "Montana", "North Carolina", "North Dakota",
                   "Nebraska", "New Hampshire", "New Jersey", "New Mexico",
                   "Nevada", "New York", "Ohio", "Oklahoma", "Oregon",
                   "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina",
                   "South Dakota", "Tennessee", "Texas", "Utah", "Virginia",
                   "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]
    api_key = "j9Z6wFdBQgxMi7hmJHFPjILBN00g0MuEyowI3Ynm"

    create_sql_tables(state_names, api_key)

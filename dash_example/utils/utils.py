"""
(la)Monty Python
Aditya Retnanto
March 2022
Module to initialize mapbox set up
"""
import json
import pandas as pd

def detail_view_init():
    """
    Opens set up json files to initialize chloropleth map
    """
    with open('data/geojson-counties-fips.json', 'r') as f:
        counties = json.load(f)
    winner = pd.read_csv("data/county_president_winner.csv", dtype={"county_fips": str})
    hurricane_path = pd.read_csv("data/hurricane_path.csv")
    with open('data/hurricane_scope.json', 'r') as f:
        hurricane_scope = json.load(f)
    hurricanes = hurricane_path['NAME'].unique()
    return counties, winner, hurricane_path, hurricane_scope, hurricanes

def get_election_year(year):
    """
    Returns election year given any year
    :param year: integer year
    """
    return year - year%4
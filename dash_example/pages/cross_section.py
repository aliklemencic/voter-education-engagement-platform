# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import json
from helper import parse_restyle
from backend import datasets

DV_NAME = 'aid_requested'
START_YEAR = 2010
END_YEAR = 2019
IV_LIST = ['black_afam', 'foreign_born','health_insurance_rate',
    'median_home_price', 'median_income', 'median_rent', 'snap_benefits', 
    'unemp_rate',  'vacant_housing_rate']
LABELS = {'black_afam':'Pcnt. Black' , 'foreign_born': 'Pcnt. Foreign Born',
    'health_insurance_rate': 'Health Iunsurance Rate',
    'median_home_price': 'Median Home Price', 'median_income': 'Median Income', 
    'median_rent': 'Median Rent', 'snap_benefits': 'Pcnt. Snap Benefits', 
    'unemp_rate': 'Unemployment Rate',  'vacant_housing_rate': 'Vacant Housing Pcnt.',
    'aid_requested': 'Aid Amount', 'incident_type': 'Disaster Type',
    'population':'Population', 'state': 'State', 'county_fips':'County FIPS Code'}
TEXAS_IDX = 43

with open('data/statestofips.json', 'r') as f:
  states_lookup = json.load(f)
  STATES = [i for i in states_lookup.keys()]

years_dict = {}
for i in range(START_YEAR, END_YEAR + 1):
    years_dict[i] = str(i)

layout = html.Div(children=[
    html.Div(className = 'filter-container',
        children=[
            html.Div(className ='filter-div', 
                children = [html.Label('Select a State'),
                    dcc.Dropdown(STATES, 
                    STATES[TEXAS_IDX], multi = True, id='state-dd')]),
            html.Div(className='filter-div',
                children = [html.Label('Select Disaster Type'),
                    dcc.Dropdown(multi = True, id='disaster-dd')]
            ),
            html.Div(className='filter-div',
                    children=[html.Label('Select X Axis Variable'),
                    dcc.Dropdown(IV_LIST, 'median_income', id='xaxis-dd')]
            )
        ]
    ),
    html.Br(),
    html.Label('Select Year Range'),
    dcc.RangeSlider(START_YEAR, END_YEAR, 1, value=[2015, 2017], 
        id='year-slider',
        marks = years_dict
    ),
    html.Br(),
    html.Div(children=[
        dcc.Graph(
            id='scatter-fig'
        )
    ]),
    html.Br(),
    html.Label('Select a range along a parallel coordinates axis to highlight points in the scatter plot.'),
    html.Div(id='pc-container', children=[
        html.Div(className='buffer'),
        html.Div(id='pc-plot',children=[
            dcc.Graph(
            id='pc-fig'
        )
        ]),
        html.Div(className='buffer')
    ]),
    dcc.Store(id='query-data'),
    dcc.Store(id='intermediate-value')
])


@callback(
    Output('query-data', 'data'),
    Input('state-dd', 'value'),
    Input('year-slider', 'value')
)
def query_api(states, years):
    '''
    Load data from FEMA and ACS APIs into app using backend modules and user
    inputs for states and years. Data is used for all visuals on cross-section
    view. If API call fails, load data from static csv as backup.
    Inputs:
        states: a list of state names selected from the states dropdown in ui
        years: a list of years selected from the years slider in ui
    Outputs:
        Joined data from FEMA and ACS data sources meeting input filter criteria,
        converted to JSON for in-browser storage.
    '''
    if not isinstance(states, list):
        states = [states]
    if not isinstance(years, list):
        years = [years]
    state_codes = [states_lookup[i] for i in states]
    try:
        # Selecting single year creates duplicate entries. Reduce to one entry.
        if max(years) == min(years):
            years = [max(years)]
        query_df = datasets.get_data(state_codes, years)
    except:
        print('API CALL FAILED - LOADING STATIC BACKUP DATA')
        df = pd.read_csv('data/harvey_test_data.csv')
        query_df = df[df['state_fips'].isin(state_codes) & 
            (df['year'] >= years[0]) &
            (df['year'] <= years[1])]
    
    return query_df.to_json(date_format='iso', orient='split')


@callback(
    Output('disaster-dd', 'options'),
    Output('disaster-dd', 'value'),
    Input('query-data','data')
)
def get_disaster_options(query_df_json):
    '''
    Get disaster options from queried data for dropdown.
    Inputs:
        query_df_json: json file from browser memory, originally created by FEMA
    
    Outputs:
        disaster_options: disaster types present in queried data, setting first
            result as default
    '''
    query_df = pd.read_json(query_df_json, orient='split')
    disaster_options = [i for i in query_df.incident_type.unique()]
    disaster_options.sort()
    return disaster_options, disaster_options[0]


@callback(
    Output('intermediate-value', 'data'),
    Input('query-data','data'),
    Input('disaster-dd', 'value'),
)
def update_data(query_df_json, disasters):
    '''
    Filter the data returned by API call further based on user inputs for
    specific disaster types.
    Inputs:
        query_df_json: json file from browser memory, originally created by FEMA
            and ACS API call
        disasters: a list of disaster types selected by user from ui dropdown
    
    Outputs:
        filtered_df: a filtered version of the original API query, which feeds
        into the parallel coordinates and scatter plot graphs, converted to
            JSON for in-browser storage
    '''
    query_df = pd.read_json(query_df_json, orient='split')
    if not isinstance(disasters, list):
        disasters = [disasters]

    filtered_df = query_df[query_df['incident_type'].isin(disasters)].reset_index(drop=True)

    return filtered_df.to_json(date_format='iso', orient='split')


@callback(
    Output('pc-fig', 'figure'),
    Input('intermediate-value', 'data')
)
def update_pc(filtered_df_json):
    '''
    Update the parallel coordinates chart with the intermediate data based on
    user selections for states, years, and disaster types.
    Inputs:
        filtered_df_json: json file from browser memory, created by
            update_pc_and_data callback
    Outputs:
        pc_fig: a Dash parallel coorinates component
    '''
    filtered_df = pd.read_json(filtered_df_json, orient='split')
    pc_fig = px.parallel_coordinates(filtered_df, color="aid_requested",
                              dimensions=IV_LIST, labels = LABELS)

    pc_fig.update_layout(margin = dict(l = 30))
    return pc_fig

@callback(
    Output('scatter-fig', 'figure'),
    Input('pc-fig', 'restyleData'),
    Input('intermediate-value', 'data'),
    Input('xaxis-dd', 'value')
)
def modify_scatter(restyleData, filtered_df_json, xaxis):
    '''
    Modify the scatter plot based on user selections for x-axis variable and
    filter data based on selected range in the parallel coordinates plot. 
    Inputs:
        restyleData: range of user selection from interactive parallel
            coordinates plot
        filtered_df_json: json file from browser memory, created by
            update_pc_and_data callback
        xaxis: the variable selected by user from ui dropdown to display on
            scatterplot x-axis
    Outputs:
        scatter_fig: a Dash scatterplot component
    '''
    filtered_df = pd.read_json(filtered_df_json, orient='split')
    # Only handles dim_range of length one and doesn't support multiple axes
    # or multiple selections along a single axis.
    if restyleData and None not in restyleData[0].values():
        dim_index, dim_range = parse_restyle.parse_restyle(restyleData)
        col_index = IV_LIST[dim_index]

        selected_points = filtered_df[(filtered_df[col_index]>=dim_range[0]) &
            (filtered_df[col_index]<=dim_range[1])].index.values
        filtered_df = filtered_df.iloc[selected_points]

    scatter_fig = px.scatter(filtered_df, x=xaxis, y="aid_requested",
        size="population", color="incident_type", hover_name='disaster_name',
        hover_data =['state', 'county_fips', 'aid_requested','population', xaxis],
        size_max=60, labels = LABELS)

    return scatter_fig
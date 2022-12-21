"""
(la)Monty Python
Aditya Retnanto
March 2022
Module to display hurricane view with choropleth and regression info
"""
import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, callback, dash_table
from utils import utils
from models.hurricane_regs import DisasterRegs

counties, winner, hurricane_path, hurricane_scope, hurricanes = utils.detail_view_init()

layout = html.Div(children=[
  html.P("Note, it might take some time to display data"),
  html.Div(children=[
        html.Label('Hurricane'),
        dcc.Dropdown(hurricanes, hurricanes[0], multi = False, id='hurricane')
    ]),
  html.Div(children=[
        html.Label('Regression Type'),
        dcc.Dropdown(['Pooled', 'Fixed Effects'], 'Pooled', multi = False, id='regression_choice')
    ]),
  html.Br(),
  html.Div([
    dcc.Graph(id='hurricane_map', style={"display": "none"})
  ]),
  html.Br(),
  html.P("Dependent variable in specified regression is dollar value requested from FEMA by county"),
  html.Div([
    dash_table.DataTable(
      id='reg_table',
      data=[]
    )
  ]),
  html.Br(),
  html.P(id = 'regression-text'),
  html.Div([
    dash_table.DataTable(
      id='var_table',
      data=[]
    )
  ])
])

@callback(
    Output("hurricane_map", 'figure'),
    Output("hurricane_map", 'style'),
    Output("reg_table", 'data'),
    Output("reg_table", 'column'),
    Output("var_table", 'data'),
    Output("var_table", 'column'),
    Output("regression-text", 'children'),
    Input('hurricane', 'value'),
    Input('regression_choice', 'value')
)
def display_hurricane(hurricane, regression_choice):
    """
    Calls API on Hurricane info, runs regression and updates figures.
    :param hurricane: User selected hurricane
    :param regression_choice: User selected regression choice
    """
    hurricane_df = hurricane_path.loc[(hurricane_path['NAME'] == hurricane)]
    regression = DisasterRegs(hurricane_scope[hurricane]["states_fips"], hurricane_scope[hurricane]["year"])
    api_data = regression.pull_data()
    if regression_choice == 'Pooled':
        reg_output,_,var_table = regression.pooled_ols(api_data)
        text = "In the table above \
        we see the results to the Pooled Ordinary Least Squares (OLS) regression. \
        This is the most simplistic, but potentially powerful regression model when looking at panel data. \
        The p-value column can be interpreted as follows: if the p-value < 0.05, it is statistically significant at the 95% Confidence level. \
        In layman’s terms, that variable is significant in determining\
        the dollar value of FEMA aid requested by the county."
    else:
        reg_output,_,var_table = regression.panel_ols(api_data)
        text = "In the table above we see the results to the Fixed Effect Panel regression, \
        where the entity effect (panel variable) is set to the state. \
        The main difference between a Fixed Effect (FE) model and Pooled OLS is that in FE the intercept of the regression \
        is allowed to vary freely across groups, in this case, across states. \
        We add this option to analyze whether different states display different characteristics in FEMA. \
        The p-value column can be interpreted as follows: if the p-value < 0.05, it is statistically significant at the 95% Confidence level. \
        In layman’s terms, that variable is significant in determining the dollar value of FEMA aid requested by the county."
    year_occur = hurricane_scope[hurricane]["year"][0]
    election = winner.loc[winner['year'] == utils.get_election_year(year_occur)]
    merged_df= pd.merge(election, api_data, how="left", on = 'county_fips')
    fig = px.choropleth_mapbox(merged_df, geojson=counties,
      locations='county_fips',
      hover_name = 'county_name',
      color = 'party',
      mapbox_style="open-street-map",
      zoom=3,
      center = {"lat": 37.0902, "lon": -95.7129},
      color_discrete_sequence=px.colors.qualitative.Set1,
      opacity=0.3,
    )
    fig.add_scattermapbox(
      lat = hurricane_df['LAT'],
      lon = hurricane_df['LON'],
      mode = 'markers+text',
      marker_size= hurricane_df['STORM_SPEED'],
      marker_color='rgb(255, 222, 113)',
      showlegend = False
    )
    return fig, {"display": "flex"}, reg_output.to_dict('records'), reg_output.columns, var_table.to_dict('records'), var_table.columns, text
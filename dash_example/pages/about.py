"""
(la)Monty Python
Aditya Retnanto
March 2022
Module to display team about me page
"""
from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
   dbc.Row([
    dbc.Col([
        html.P('Aditya Retnanto'),
        html.Img(
            src='assets/profilepics/aditya_pic.jpg',
            height = 200),
        html.P('Merge Conflict Resolver'),
        html.A('LinkedIn', href="https://www.linkedin.com/in/adityaretnanto/")
    ]),
    dbc.Col([
        html.P('Ali Klemencic'),
        html.Img(
            src='assets/profilepics/ali_pic.jpeg',
            height = 200),
        html.P('Founder CTO'),
        html.A('LinkedIn', href="https://www.linkedin.com/in/alisonklemencic/")
   ])
   ]),
   dbc.Row([
    dbc.Col([
        html.Br(),
        html.P('Wesley Janson'),
        html.Img(
            src='assets/profilepics/wesley_pic.jpg',
            height = 200),
        html.P('Chief Statistician'),
        html.A('LinkedIn', href="https://www.linkedin.com/in/wesley-janson/")
    ]),
    dbc.Col([
        html.Br(),
        html.P('Zander Meitus'),
        html.Img(
            src='assets/profilepics/zander_pic.jpg',
            height = 200 ),
            html.P('SDE Intern'),
        html.A('LinkedIn', href="https://www.linkedin.com/in/zander-meitus/")
    ])
    ])
])
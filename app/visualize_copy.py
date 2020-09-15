# add mongo and postgre to path so that the python files can be imported
import sys
sys.path.insert(1, '../mongo')
sys.path.insert(2, '../postgre')

import word_freqs
import postgre_connection
import mongodb_connection
# need to install
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
# in python
import random

############################################## INITIALIZATION #############################################
# connect to postgre
psql=postgre_connection.connect_to_postgre('../config/database_config.json')
psql.connect_to_db()
# get columns (assumed that they are the same for all tables, which is currently true)
query="""SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='AZN';"""
res=psql.engine.execute(query).fetchall()
psql_columns=[col[0] for col in res]

mongo=mongodb_connection.connect_to_mongodb('../config/database_config.json',database_name='news')
mongo.connect_to_db()

################################################# APP #############################################
# the actual app
app = dash.Dash(__name__,title='MyApp')
################################################ LAYOUT #############################################
app.layout = html.Div(children=[
    html.Div(children=[
    html.H1(children='MyApp'),

    html.Div(children='''
    Most frequent words used in Reuters, MarketWatch and Financial Times sitemap.xml file article titles are visualized in the first figure.
    One can examine either titles or tickers aggregated on a given time interval. N most common results can be shown.
    '''),
    html.Div(children='''
    In the second figure trades of a stock in London Stock Exchange (that was mentioned in the sitemaps) are shown with some articles
    related to it. One can choose between different stocks and choose which attribute is on the y-axis or as the color. Hovering
    over star shaped markers reveal the article titles.
    '''),
    ],
    className='allText'
    ),
############################################## TRADE FIGURE #############################################
    # dropdown to choose which company is in the london figure
    html.Div('Choose equity/ETF shown',className='allText'),
    dcc.Dropdown(
    id='london-asset-dropdown',
    options=[{'label': i, 'value': i} for i in psql.tables],
    value=psql.tables[0],
    className='dropdown',
    clearable=False
    ),
    html.Div(id='london-stock-dropdown-output'),
    # choose y-axis data shown
    html.Div('Filter data based on',className='allText'),
    dcc.Dropdown(
    id='london-asset-filter-dropdown',
    options=[{'label': i, 'value': i} for i in psql_columns],
    value=psql_columns[0],
    className='dropdown',
    clearable=True,
    multi=True
    ),
    html.Div(id='london-asset-filter-dropdown'),
    # choose color data
    html.Div('Choose attribute shown as color',className='allText'),
    dcc.Dropdown(
    id='london-stock-color-dropdown',
    options=[{'label': i, 'value': i} for i in lon_cols],
    value='volume',
    className='dropdown',
    clearable=False
    ),
    html.Div(id='london-stock-color-dropdown-output'),
    # placeholder for graph
    dcc.Graph(
        id='london-graph'
    ),
])
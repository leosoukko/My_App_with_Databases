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
class create_app:
    def __init__(self,config_file):
        self.config_file=config_file

    def connect_to_db(self):
        # connect to postgre
        self.psql=postgre_connection.connect_to_postgre(self.config_file)
        self.psql.connect_to_db()
        # get columns (assumed that they are the same for all tables, which is currently true)
        query="""SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='{}';""".format(psql.tables[0])
        res=psql.engine.execute(query).fetchall()
        self.psql_columns=[col[0] for col in res]
        # connect to mongo
        self.mongo=mongodb_connection.connect_to_mongodb(self.config_file,database_name='news')
        self.mongo.connect_to_db()

################################################ LAYOUT #############################################
def create_layout()

################################################# APP #############################################
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
    html.Div(id='london-asset-dropdown-output'),
    # Filter data
    html.Div('Filter data based on columns',className='allText'),
    london_filters=[]
    for col in psql_columns:
            html.Div(dcc.Dropdown(
            id='london-asset-filter-dropdown'.format(col),
            options=[{'label': i, 'value': i} for i in psql_columns],
            value=psql_columns[0],
            className='dropdown',
            clearable=True
            ),
            html.Div(id='london-asset-filter-dropdown-output'.format(col)))
    # placeholder for graph
    dcc.Graph(
        id='london-graph'
    )
])
############################################## CALLBACKS #############################################
############################################## TRADE FIGURE #############################################
@app.callback(Output('word-graph','figure'),
[Input('word-freq-dropdown','value'),
Input('word-freq-time-interval','value'),
Input('word-freq-top-n','value'),])
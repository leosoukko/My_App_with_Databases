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
import datetime

############################################## INITIALIZATION #############################################
config_file='../config/database_config.json'

psql=postgre_connection.connect_to_postgre(config_file)
psql.connect_to_db()
# get columns (assumed that they are the same for all tables, which is currently true)
query="""SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='{}';""".format(psql.tables[0])
res=psql.engine.execute(query).fetchall()
psql_columns=[col[0] for col in res]
# connect to mongo
mongo=mongodb_connection.connect_to_mongodb(config_file)
mongo.connect_to_db()

################################################# APP #############################################
app = dash.Dash(__name__,title='MyApp')
################################################ LAYOUT #############################################
app.layout = html.Div(children=[
    html.Div(children=[
    html.H1(children='MyApp'),

    html.Div(children='''
    
    '''),
    html.Div(children='''
    
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
    # date range start
    html.Div("""
    Filter data with starting and ending dates (format YYYY-MM-DD HH:MM:SS)<br>
    And with minimum and maximum volumes
    """,className='allText'),
    dcc.Input(
        id='london-start-date',
        type='text',
        value='2020-09-01 00:00:00',
        className='writable_input',
        debounce=True
    ),
    # date range end
    dcc.Input(
        id='london-end-date',
        type='text',
        value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        className='writable_input',
        debounce=True
    ),
    # filter based on volume
    dcc.Input(
        id='london-volume-filter-min',
        type='number',
        value=1,
        min=1,
        className='writable_input',
        debounce=True
    ),
    dcc.Input(
        id='london-volume-filter-max',
        type='number',
        value=100000,
        min=2,
        className='writable_input',
        debounce=True
    ),
    # placeholder for graph
    dcc.Graph(
        id='london-graph'
    )
])
############################################## CALLBACKS #############################################
############################################## TRADE FIGURE #############################################
@app.callback(Output('london-graph','figure'),
[Input('london-asset-dropdown','value'),
Input('london-start-date','value'),
Input('london-end-date','value'),
Input('london-volume-filter-min','value'),
Input('london-volume-filter-max','value')])

# update the figure
def update_london_fig(assetName,startDate,endDate,volumeMin,volumeMax):
    # make a query to postgre db
    query="""
    SELECT * FROM "{}" WHERE "tradeTime">='{}' AND "tradeTime"<='{}' AND "volume">={} AND "volume"<={} ORDER BY "tradeTime" DESC;
    """.format(assetName,startDate,endDate,volumeMin,volumeMax)
    df=pd.read_sql(query,con=psql.engine,index_col=['tradeTime'])
    df.index=pd.to_datetime(df.index)

    # make the figure
    fig = go.Figure(go.Scattergl(x=df.index,y=df['price'],marker_color=df['volume'],mode='markers',
    marker=dict(colorscale='Bluered',showscale=True),text=df['volume'],
    hovertemplate='price: %{y}'+'<br>time : %{x}<br>volume: %{text}'))
    # layout
    fig.update_layout(title=dict(text=assetName,x=0.5,y=0.87))
    #fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    fig.update_yaxes(title_text='price')
    fig.update_xaxes(nticks=31,tickangle=300)

    return fig

############################################################### DEBUG #############################################
if __name__ == '__main__':
    app.run_server(debug=True)
# add mongo and postgre to path so that the python files can be imported
import sys
from pathlib import Path
root_dir_of_app=str(Path(__file__).resolve().parents[1])
sys.path.insert(1, root_dir_of_app+'\mongo')
sys.path.insert(2, root_dir_of_app+'\postgre')

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
config_file=root_dir_of_app+"\config\database_config.json"

# connect to postgre
psql=postgre_connection.connect_to_postgre(config_file)
psql.connect_to_db()
# function to get unique values for given asset and column. Will be used to interactively change filtering options for different assets
def get_unique_values(tbl,col,start,end):
    query="""SELECT DISTINCT "{}" FROM "{}" WHERE "tradeTime">='{}' AND "tradeTime"<='{}';""".format(col,tbl,start,end)
    res=psql.engine.execute(query).fetchall()
    unique_values=[vals[0] for vals in res]
    unique_options=[{'label': i, 'value': i} for i in unique_values]
    return unique_values,unique_options

# connect to mongo
#mongo=mongodb_connection.connect_to_mongodb(config_file)
#mongo.connect_to_db()

################################################# APP #############################################
app = dash.Dash(__name__,title='MyApp')
################################################ LAYOUT #############################################
app.layout = html.Div(children=[
    html.Div(children=[
    html.H1(children='MyApp'),

    html.Div(children='''
    This App shows all trades gathered in PostgreSQL database for given asset. Multiple different filters for the data are availble.
    Color of the marker refers to trade volume.
    '''),
    html.Div(children='''
    Next step might be to query MongoDB for news articles related to the asset, but most likely there aren't many articles.
    '''),
    html.Br()
    ],
    className='allText'
    ),
############################################## TRADE FIGURE #############################################
    # dropdown to choose which company is in the london figure
    html.Div('Choose Equity/ETF shown',className='allText'),
    dcc.Dropdown(
    id='london-asset-dropdown',
    options=[{'label': i, 'value': i} for i in psql.tables],
    value=psql.tables[0],
    className='dropdown',
    clearable=False
    ),
    # date picker
    html.Div('Choose starting and ending dates (afterwards you can zoom more in the figure if wanted)',className='allText'),
    dcc.DatePickerRange(
        id='london-date-picker-range',
        start_date=datetime.datetime.now().date(),
        end_date=(datetime.datetime.now() + datetime.timedelta(1)).date(),
        clearable=False,
        display_format ='YYYY-MM-DD',
        className='dropdown'
    ),
    html.Div(id='london-date-picker-range-output'),
    # date range start
    html.Div("""
    Filter data with minimum and maximum volumes. Negative volume refers to cancelled trade.
    """,className='allText'),
    # filter based on volume
    dcc.Input(
        id='london-volume-filter-min',
        placeholder='Minimum volume',
        type='number',
        className='writable_input',
        debounce=True
    ),
    dcc.Input(
        id='london-volume-filter-max',
        placeholder='Maximum volume',
        type='number',
        className='writable_input',
        debounce=True
    ),
    # dropdown to filter by currency
    html.Div('Filter data by currency',className='allText'),
    dcc.Dropdown(
    id='london-currency-dropdown',
    className='dropdown',
    clearable=False,
    multi=True
    ),
    # dropdown to filter by type
    html.Div('Filter data by type',className='allText'),
    dcc.Dropdown(
    id='london-type-dropdown',
    className='dropdown',
    clearable=False,
    multi=True
    ),
    # dropdown to filter by currency
    html.Div('Filter data by Mic-Codes',className='allText'),
    dcc.Dropdown(
    id='london-micCode-dropdown',
    className='dropdown',
    clearable=False,
    multi=True
    ),
    # dropdown to filter by currency
    html.Div('Filter data by TradeTypes',className='allText'),
    dcc.Dropdown(
    id='london-tradeType-dropdown',
    className='dropdown',
    clearable=False,
    multi=True
    ),
    # placeholder for graph
    dcc.Graph(
        id='london-graph'
    )
])
############################################## CALLBACKS #############################################
###################################### DROPDOWNS BASED ON ASSET #############################################
@app.callback(
[Output('london-volume-filter-min','value'),Output('london-volume-filter-max','value'),
Output('london-currency-dropdown','options'),Output('london-currency-dropdown','value'),
Output('london-type-dropdown','options'),Output('london-type-dropdown','value'),
Output('london-micCode-dropdown','options'),Output('london-micCode-dropdown','value'),
Output('london-tradeType-dropdown','options'),Output('london-tradeType-dropdown','value')],
[Input('london-asset-dropdown','value'),
Input('london-date-picker-range','start_date'),
Input('london-date-picker-range','end_date'),])

def update_options(assetName,start,end):
    # use the function in initialization to get unique values for the columns in dash format
    type_vals,type_options=get_unique_values(assetName,'type',start,end)
    currency_vals,currency_options=get_unique_values(assetName,'currency',start,end)
    micCode_vals,micCode_options=get_unique_values(assetName,'micCode',start,end)
    tradeType_vals,tradeType_options=get_unique_values(assetName,'tradeType',start,end)
    # get min and max volumes
    query="""SELECT MIN("volume") FROM "{}" WHERE "tradeTime">='{}' AND "tradeTime"<='{}';""".format(assetName,start,end)
    min_vol=psql.engine.execute(query).fetchall()[0][0]
    query="""SELECT MAX("volume") FROM "{}" WHERE "tradeTime">='{}' AND "tradeTime"<='{}';""".format(assetName,start,end)
    max_vol=psql.engine.execute(query).fetchall()[0][0]

    return min_vol,max_vol,currency_options,currency_vals,type_options,type_vals,micCode_options,micCode_vals,tradeType_options,tradeType_vals

############################################## TRADE FIGURE #############################################
@app.callback(Output('london-graph','figure'),
[Input('london-asset-dropdown','value'),
Input('london-date-picker-range','start_date'),
Input('london-date-picker-range','end_date'),
Input('london-volume-filter-min','value'),
Input('london-volume-filter-max','value'),
Input('london-currency-dropdown','value'),
Input('london-type-dropdown','value'),
Input('london-micCode-dropdown','value'),
Input('london-tradeType-dropdown','value')])

# update the figure
def update_london_fig(assetName,startDate,endDate,volumeMin,volumeMax,currency,TYPE,micCode,tradeType):
    # avoid errors from empty inputs (also could just make the inputs non-clearable, but then the placeholder wont show)
    if volumeMin==None:
        volumeMin=1
    if volumeMax==None:
        volumeMax=100000
    
    # join the options for SQL query
    currency="','".join(currency)
    TYPE="','".join(TYPE)
    micCode="','".join(micCode)
    tradeType="','".join(tradeType)

    # make a query to postgre db
    query="""
    SELECT * FROM "{}" WHERE "tradeTime">='{}' AND "tradeTime"<='{}' AND "volume">={} AND "volume"<={} AND "currency" IN ('{}')
    AND "type" IN ('{}') AND "micCode" IN ('{}') AND "tradeType" IN ('{}') ORDER BY "tradeTime" DESC;
    """.format(assetName,startDate,endDate,volumeMin,volumeMax,currency,TYPE,micCode,tradeType)
    df=pd.read_sql(query,con=psql.engine,index_col=['tradeTime'])
    df.index=pd.to_datetime(df.index)

    # make the figure
    fig = go.Figure(go.Scattergl(x=df.index,y=df['price'],marker_color=df['volume'],mode='markers',
    marker=dict(colorscale='Bluered',showscale=True),name='Trades',
    text=df['volume'].astype(str)+'<br>type: '+df['type'].astype(str)+'<br>currency: '+df['currency'].astype(str)+'<br>micCode: '+df['micCode'].astype(str)+'<br>tradeType: '+df['tradeType'].astype(str),
    hovertemplate='price: %{y}'+'<br>time : %{x}<br>volume: %{text}'))
    # layout
    fig.update_layout(title=dict(text=assetName,x=0.5,y=0.87))
    #fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    fig.update_yaxes(title_text='Price')
    fig.update_xaxes(nticks=31,tickangle=300)

    return fig

######################################################### DEBUG #############################################
if __name__ == '__main__':
    app.run_server(debug=True)
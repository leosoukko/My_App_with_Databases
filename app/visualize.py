# add mongo and postgre to path so that the python files can be imported
import sys
sys.path.insert(1, '../mongo')
sys.path.insert(2, '../postgre')

import word_freqs
import london_stock_data
# need to install
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
# in python
import random

############################################################### INITIALIZATION #############################################
# initialize sitemap word freq options
cols=['title','tickers']
# create object which counts the words from keywords.json, do not count yet
write_file='data/word_freqs.csv'
read_file='data/keywords.json'
wf=word_freqs.sitemap_word_freq(interval=120,top_n=3,colName='tickers',read_file='data/keywords.json')
wf.read_data()
# create object which fetches london stock exchange dat, do not fetch yet
lon=london_stock_data.londonstockexchange('data/keywords.json')
lon.get_london_stocks()
lon_cols=['price','volume','tradeValue']

############################################################### APP #############################################
# the actual app
app = dash.Dash(__name__,title='Sitemap Data Viz')
############################################################### LAYOUT #############################################
app.layout = html.Div(children=[
    html.Div(children=[
    html.H1(children='Financial News Sitemaps'),

    html.Div(children='''
    Most frequent words used in Reuters, MarketWatch and Financial Times sitemaps are visualized in the first figure.
    One can examine either titles, keywords or tickers aggregated on a given time interval. N most common results can be shown.
    '''),
    html.Div(children='''
    In the second figure trades of a stock in London Stock Exchange (that was mentioned in the sitemaps) are shown with some articles
    related to it. One can choose between different stocks and choose which attribute is on the y-axis or as the color. Hovering
    over star shaped markers reveal the article titles.
    '''),
    ],
    className='allText'
    ),
############################################################### FIGURE 1 #############################################
    # dropdown to choose what data is in the sitemap word figure
    html.Div('Choose tag shown',className='allText'),
    dcc.Dropdown(
    id='word-freq-dropdown',
    options=[{'label': i, 'value': i} for i in cols],
    value='tickers',
    className='dropdown',
    clearable=False
    ),
    html.Div(id='word-freq-dropdown-output'),
    # choose aggregation time
    html.Div('Time interval to aggregate articles (minutes)',className='allText'),
    dcc.Input(
        id='word-freq-time-interval',
        type='number',
        value=120,
        step=10,
        className='writable_input'
    ),
    # choose top n
    html.Div('N most common words shown',className='allText'),
    dcc.Input(
        id='word-freq-top-n',
        type='number',
        value=3,
        className='writable_input'
    ),
    # placeholder for graph
    dcc.Graph(
        id='word-graph'
    ),
############################################################### FIGURE 2 #############################################
    # dropdown to choose which company is in the london figure
    html.Div('Choose company shown',className='allText'),
    dcc.Dropdown(
    id='london-stock-dropdown',
    options=[{'label': i, 'value': i} for i in lon.lon_tickNames],
    value=lon.stockName,
    className='dropdown',
    clearable=False
    ),
    html.Div(id='london-stock-dropdown-output'),
    # choose y-axis data shown
    html.Div('Choose attribute shown on y-axis',className='allText'),
    dcc.Dropdown(
    id='london-stock-column-dropdown',
    options=[{'label': i, 'value': i} for i in lon_cols],
    value='price',
    className='dropdown',
    clearable=False
    ),
    html.Div(id='london-stock-column-dropdown-output'),
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
############################################################### CALLBACKS #############################################
############################################################### FIGURE 1 #############################################
@app.callback(Output('word-graph','figure'),
[Input('word-freq-dropdown','value'),
Input('word-freq-time-interval','value'),
Input('word-freq-top-n','value'),])
# update the figure based on chosen data type
def update_word_fig(colName,interval,top_n):
    # count the word frequencies with given params
    wf.word_frequency(interval,top_n,colName)
    # get the data
    data=wf.df
    # the actual figure
    fig = go.Figure()
    col_ind=1
    i=1
    # loop through all columns that hold values (every other column holds values, every other holds keyname)
    while col_ind<=data.shape[1]:
        # add some noise so that words with same freqs will be apart
        y_rand=random.uniform(-0.15,0.15)
        # create scatter
        fig.add_trace(go.Scatter(x=data.index,y=data.iloc[:,col_ind]+y_rand,name='Top {}'.format(i),mode='markers+text',
        text=data.iloc[:,col_ind-1],textposition="top center",hoverinfo='x+text'))
        # update value columns and iteration number
        col_ind+=2
        i+=1
    # layout
    fig.update_layout(title=dict(text='Sitemaps: Most frequent words',x=0.45,y=0.87))
    fig.update_yaxes(title_text='Frequency',nticks=20)
    fig.update_xaxes(nticks=31,tickangle=300)

    return fig

############################################################### FIGURE 2 #############################################
@app.callback(Output('london-graph','figure'),
[Input('london-stock-dropdown','value'),
Input('london-stock-column-dropdown','value'),
Input('london-stock-color-dropdown','value'),])
# update the figure
def update_london_fig(stockName,colName,colorName):
    # get trades for this stock
    lon.get_trade_data(stockName)
    # data
    df=lon.df
    # make the figure
    fig = go.Figure(go.Scattergl(x=df.index,y=df[colName],marker_color=df[colorName],name=colName,mode='markers',
    marker=dict(colorscale='Bluered',showscale=True),text=df[colorName],
    hovertemplate='%{y}'+'<br>time : %{x}<br>'+colorName+' : %{text}'))
    # add the articles of the stock in the figure
    fig.add_trace(go.Scatter(x=lon.lon_news_df.index,y=[df[colName].min()]*lon.lon_news_df.shape[0],
    text=lon.lon_news_df['link'],hoverinfo='x+text',mode='markers',marker_symbol='star',name='Article'))
    # layout
    fig.update_layout(title=dict(text=stockName,x=0.5,y=0.87),hovermode='x unified')
    fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    fig.update_yaxes(title_text=colName)
    fig.update_xaxes(nticks=31,tickangle=300)

    return fig
############################################################### DEBUG #############################################
if __name__ == '__main__':
    app.run_server(debug=True)

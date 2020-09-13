# need to install
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
# in python
from collections import Counter
from io import StringIO
import datetime

class london_stock_exchange:
    def __init__(self,stock_file):
        self.stock_file=stock_file

    def get_trade_data(self,stockName=False,interval=1):
        # if stock tick is not given in visualize.py
        if stockName==False:
            # biggest key (most frequent stock)
            stockName=self.stockName
        # get data from API
        site=requests.get('https://api.londonstockexchange.com/api/gw/lse/download/{}/trades'.format(stockName))
        if site.ok:
            # data as df, limit the data for this date (overnight trades not available)
            self.df=pd.read_csv(StringIO(site.text),index_col=0)
            self.df.index=pd.to_datetime(self.df.index)
            now=pd.to_datetime(datetime.date.today())
            self.df=self.df[self.df.index>=now]
            # change correct GBPX to GBP and get only trades in pounds
            self.df.loc[(self.df['currency']=='GBX'),'price']=self.df.loc[(self.df['currency']=='GBX'),'price']/100.0
            self.df=self.df[(self.df['currency']=='GBP') | (self.df['currency']=='GBX')]
            # need to drop the first trade of the day because it has much higher volume than other trades
            self.df=self.df.drop(self.df['volume'].idxmax(),axis=0)

            # news articles of this stock, limit for this date
            self.lon_news_df=pd.DataFrame(self.lon_news[stockName])
            self.lon_news_df.index=self.lon_news_df['date']
            self.lon_news_df=self.lon_news_df.drop(columns=['date'])
            self.lon_news_df.index=pd.to_datetime(self.lon_news_df.index)

            print('Fetched',stockName,': df size',self.df.shape)
        else:
            del self.lon_tickFreqs[stockName]
            self.lon_tickNames.remove(stockName)
            print('Failed to fetch trade data')

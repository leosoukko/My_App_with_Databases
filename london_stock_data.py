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

    def read_stock_ticks(self):
        self.stocks=pd.read_csv(self.stock_file,header=None).iloc[:,0].values

    def get_trade_data(self):
        for stock in self.stocks:
            # get data from API
            site=requests.get('https://api.londonstockexchange.com/api/gw/lse/download/{}/trades'.format(stock))
            if site.ok:
                # data as df, limit the data for this date (overnight trades not available)
                self.df=pd.read_csv(StringIO(site.text),index_col=0)
                self.df.index=pd.to_datetime(self.df.index)
                now=pd.to_datetime(datetime.date.today())
                self.df=self.df[self.df.index>=now]
                # change GBX to GBP and get only trades in pounds
                self.df.loc[(self.df['currency']=='GBX'),'price']=self.df.loc[(self.df['currency']=='GBX'),'price']/100.0
                self.df['currency'][self.df['currency']=='GBX']='GBP'
                #self.df=self.df[(self.df['currency']=='GBP') | (self.df['currency']=='GBX')]

                print('Fetched',stock,': df size',self.df.shape)
            else:
                print('Failed to fetch trade data')

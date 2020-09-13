# need to install
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
# in python
from collections import Counter
from io import StringIO
import datetime

class londonstockexchange:
    def __init__(self,sitemap_filename):
        self.sitemap_filename=sitemap_filename
        self.lon_ticks=[]
        self.lon_news={}
        self.data_list={}

    def read_sitemap_json(self):
        self.df=pd.read_json(self.sitemap_filename).T
        self.df=self.df.set_index('date')
        self.df.index=pd.to_datetime(self.df.index)
        self.df=self.df.sort_index().tz_localize(None)
        # limit the data for this date
        now=pd.to_datetime(datetime.date.today())
        self.df=self.df[self.df.index>=now]

    def get_london_stocks(self):
        # get the keywords
        self.read_sitemap_json()
        # skip empty tickers
        self.df=self.df[self.df['tickers'].str.len()>1]
        # for each ticker list
        for row_ind,row in enumerate(self.df['tickers']):
            # for each ticker in the list of one article's tickers
            for tick in row:
                # get the ticker if it is in London Stock Exchange
                if 'lon:' in tick:
                    tick=tick.split(':')[1].upper()
                    self.lon_ticks.append(tick)
                    # also get the news' date and link (formatted)
                    # if the ticker already exists in the dictionary just append link and date
                    if tick in self.lon_news:
                        self.lon_news[tick]['link'].append(self.df.iloc[row_ind,:]['link'].split('/')[-1].replace('-',' '))
                        self.lon_news[tick]['date'].append(self.df.index[row_ind])
                    # if does not exist then also initialize
                    else:
                        self.lon_news[tick]={}
                        self.lon_news[tick]['link']=[]
                        self.lon_news[tick]['date']=[]
                        self.lon_news[tick]['link'].append(self.df.iloc[row_ind,:]['link'].split('/')[-1].replace('-',' '))
                        self.lon_news[tick]['date'].append(self.df.index[row_ind])

        # count the frequencies and get unique tickNames
        self.lon_tickFreqs=dict(Counter(self.lon_ticks))
        self.lon_tickNames=list(set(self.lon_ticks))
        # initialize stockname as most common tick, will be used in get_trade_data
        self.stockName=max(self.lon_tickFreqs, key=self.lon_tickFreqs.get)

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

            # may need to aggregate data if there are too many trades
            # price=self.df.groupby(pd.Grouper(freq='{}S'.format(interval))).mean()['price']
            # TV=self.df.groupby(pd.Grouper(freq='{}S'.format(interval))).mean()['tradeValue']
            # volume=self.df.groupby(pd.Grouper(freq='{}S'.format(interval))).sum()['volume']
            # self.df=pd.DataFrame([price,TV,volume]).T
            # self.df.columns=['price','tradeValue','volume']
            # self.df=self.df.dropna()

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

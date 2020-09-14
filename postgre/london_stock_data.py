# my files
import postgre_connection
# need to install
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
# in python
from collections import Counter
from io import StringIO
import datetime
import time
import random

class london_stock_exchange:
    def __init__(self,config_file,stock_file):
        self.config_file=config_file
        self.stock_file=stock_file

    def read_stock_ticks(self):
        self.stocks=pd.read_csv(self.stock_file,header=None).iloc[:,0].values

    def connect_to_db(self):
        self.psql=postgre_connection.connect_to_postgre(self.config_file)
        self.psql.connect_to_db()

    def use_LSE_API(self,stock):
        # get data from API
        site=requests.get('https://api.londonstockexchange.com/api/gw/lse/download/{}/trades'.format(stock))
        if site.ok:
            # data as df
            try:
                self.df=pd.read_csv(StringIO(site.text))
                self.df['tradeTime']=pd.to_datetime(self.df['tradeTime'])
                # change GBX to GBP
                self.df.loc[(self.df['currency']=='GBX'),'price']=self.df.loc[(self.df['currency']=='GBX'),'price']/100.0
                self.df.loc[(self.df['currency']=='GBX'),'currency']='GBP'
                # drop column that can be calculated from other cols
                self.df=self.df.drop(columns=['tradeValue'])
                # group observations that are otherwise duplicates but have just different volume
                self.df=self.df.groupby(['tradeTime','currency','price','type','micCode','tradeType'],as_index=False)['volume'].sum()
                self.df=self.df.drop_duplicates(subset=['tradeTime','currency','price','type','micCode','tradeType'])
                self.df=self.df.sort_values(by='tradeTime',ascending=False)

                print('Fetched',stock,': df size',self.df.shape)
                return True
            except:
                print('No trades')
                return False
        else:
            print('Failed to fetch trade data')
            return False

    def query_postgre(self,stock):
        # max tradetime
        query='SELECT MAX("tradeTime") FROM "{}";'.format(stock)
        max_date=self.psql.engine.execute(query).fetchall()
        self.max_date=max_date[0][0]
        # if no records exist, then initialize
        if self.max_date==None:
            self.max_date=datetime.datetime(1970,1,1)
        # print how many rows this stock currently has
        query='SELECT COUNT(price) FROM "{}";'.format(stock)
        n_rows=self.psql.engine.execute(query).fetchall()
        print('Before inserting table has',n_rows[0][0],'rows')

    def get_trade_data(self):
        # read the stocks that are queried
        self.read_stock_ticks()
        # connect to postrgesql
        self.connect_to_db()
        # for each stock
        for stock in self.stocks:
            # check if table for this stock/equity/asset already exists, if not then create table
            if stock not in self.psql.tables:
                print('Creating new table for',stock)
                query="""
                CREATE TABLE "{}" ("tradeTime" TIMESTAMP NOT NULL, currency VARCHAR(4), price NUMERIC(12,6), volume INTEGER, 
                type VARCHAR(16), "micCode" VARCHAR(16), "tradeType" VARCHAR(16));
                """.format(stock)
                self.psql.engine.execute(query)
            # get data from API
            success=self.use_LSE_API(stock)
            # if it worked
            if success:
                # get most recent trades already in db
                self.query_postgre(stock)
                # get only more recent trades than those already in the DB
                self.df=self.df[self.df['tradeTime']>pd.to_datetime(self.max_date)]
                # insert to db
                self.df.to_sql(stock, con=self.psql.engine, if_exists='append', index=False)
                # check rows after inserting
                query='SELECT COUNT(price) FROM "{}";'.format(stock)
                n_rows=self.psql.engine.execute(query).fetchall()
                print('After inserting table has',n_rows[0][0],'rows')
                print('')
                # sleep
                time.sleep(random.uniform(6.66,9.99))

lse=london_stock_exchange('../config/database_config.json',"london_stocks.txt")
lse.get_trade_data()


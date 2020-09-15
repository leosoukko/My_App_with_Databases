# in python
from collections import Counter
# need to install
import pandas as pd
import numpy as np

class sitemap_word_freq:
    def __init__(self,interval,top_n,colName,read_file):
        self.interval=interval#time interval for aggregating news
        self.top_n=top_n#top_n words to show
        self.colName=colName#title or keyword etc
        self.read_file=read_file
        self.output={}

    def read_data(self):
        self.df=pd.read_json(self.read_file).T
        self.df=self.df.set_index('date')
        self.df.index=pd.to_datetime(self.df.index)
        self.df=self.df.sort_index()
        
    def word_frequency(self,interval=False,top_n=False,colName=False):
        # if the information is given in visualize.py, then override
        if interval:
            self.interval=interval
            self.top_n=top_n
            self.colName=colName
        # get the data
        self.read_data()
        # group data by time interval and get the column wanted
        self.grouped_df=self.df.groupby(pd.Grouper(freq='{}min'.format(self.interval))).sum()[self.colName]
        # get rid of time intervals without news
        self.grouped_df=self.grouped_df[self.grouped_df!=0]
        # for each row (time group)
        for row_ind,row in enumerate(self.grouped_df):
            # get the n most common words and their frequencies (skip empty entries)
            freqs=Counter([r for r in row if r!='']).most_common(self.top_n)
            # uneven number of elements will result in error for dataframes
            while len(freqs)<self.top_n:
                freqs.append((None,None))
            # initialize output
            self.output[self.grouped_df.index[row_ind].strftime('%Y-%m-%d %H:%M:%S')]=[]
            # for each word frequency pair
            for top_i in range(len(freqs)):
                # save them as separate values
                self.output[self.grouped_df.index[row_ind].strftime('%Y-%m-%d %H:%M:%S')].append(freqs[top_i][0])#key
                self.output[self.grouped_df.index[row_ind].strftime('%Y-%m-%d %H:%M:%S')].append(freqs[top_i][1])#value

        # as df
        self.df=pd.DataFrame(self.output).T


# my files
import news_sitemap
# need to install
import pandas as pd
# in python
import sys
import json

class controller:
    def __init__(self,sitemap_file):
        self.sitemap_file=sitemap_file
        self.data={}

    def get_sitemaps(self):
        self.URLS=pd.read_csv(self.sitemap_file,header=None).iloc[:,0].values

    def fetch_data(self):
        # get the sitemap URLS
        self.get_sitemaps()
        for url in self.URLS:
            # MW has different tags than other sites
            if url=='https://www.marketwatch.com/mw_news_sitemap.xml':
                sitemap_obj=news_sitemap.get_sitemap_data(url,['update','says','us'],'n','../config/database_config.json')
            else:
                sitemap_obj=news_sitemap.get_sitemap_data(url,['update','says','us'],'news','../config/database_config.json')
            # get and update data
            sitemap_obj.get_and_update_data()

cntrl=controller('sitemaps.txt')
cntrl.fetch_data()

# my files
import news_sitemap
import word_freqs
# need to install
import pandas as pd
# in python
import sys
import json

class controller:
    def __init__(self,URLS,filename):
        self.URLS=URLS
        self.filename=filename
        self.data={}

    def write_data(self):
        with open(self.filename,'w') as f:
            json.dump(self.data,f)

    def fetch_data(self):
        for url in self.URLS:
            print(url)
            # MW has different tags than other sites
            if url=='https://www.marketwatch.com/mw_news_sitemap.xml':
                sitemap_obj=news_sitemap.get_sitemap_data(url,['update','says','us'],'n')
            else:
                sitemap_obj=news_sitemap.get_sitemap_data(url,['update','says','us'],'news')
            # get the data and update the dict
            sitemap_obj.get_data()
            self.data.update(sitemap_obj.output)
        
        self.write_data()

URLS=['https://www.marketwatch.com/mw_news_sitemap.xml',
'https://www.reuters.com/sitemap_news_index1.xml',
'https://www.reuters.com/sitemap_news_index2.xml',
'https://www.ft.com/sitemaps/news.xml']
# use the controller to get all data form sitemaps and combine them
cntrl=controller(URLS,'data/keywords.json')
cntrl.fetch_data()
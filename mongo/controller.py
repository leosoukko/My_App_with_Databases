# my files
import news_sitemap
import mongodb_connection
# need to install
import pandas as pd
# in python
import sys
import json
from pathlib import Path

class controller:
    def __init__(self,sitemap_file,config_file):
        self.db_config_file=config_file
        self.sitemap_file=sitemap_file
        self.data={}
    
    def connect_to_db(self):
        self.mongodb_connection=mongodb_connection.connect_to_mongodb(self.db_config_file)
        self.mongodb_connection.connect_to_db()

    def get_sitemaps(self):
        self.URLS=pd.read_csv(self.sitemap_file,header=None).iloc[:,0].values

    def fetch_data(self):
        # connect to the database
        self.connect_to_db()
        # get the sitemap URLS
        self.get_sitemaps()
        # for each sitemap.xml file
        for url in self.URLS:
            # MW has different tags than other sites
            if url=='https://www.marketwatch.com/mw_news_sitemap.xml':
                sitemap_obj=news_sitemap.get_sitemap_data(url,['update','says','us'],'n',self.mongodb_connection)
            else:
                sitemap_obj=news_sitemap.get_sitemap_data(url,['update','says','us'],'news',self.mongodb_connection)
            # get and update data
            sitemap_obj.get_and_update_data()

# get correct directiories where ever the script is run from
root_dir_of_app=str(Path(__file__).resolve().parents[1])
# create object
cntrl=controller(root_dir_of_app+'\mongo\sitemaps.txt',root_dir_of_app+'\config\database_config.json')
cntrl.fetch_data()

from pymongo import MongoClient

import json

class connect_to_mongodb:
    def __init__(self,config_file,database_name):
        self.db_name=database_name
        self.config_file=config_file

    def read_config_file(self):
        with open(self.config_file,'r') as json_file:
            self.config=json.load(json_file)

    def connect_to_db(self):
        # read conf file
        self.read_config_file()
        # connect to db
        self.client=MongoClient(self.config['MongoDB']['URI'])
        self.db=self.client[self.db_name]
        self.collections=self.db.list_collection_names()
        print('Connected to MongoDB')
        print('Current collections:',self.collections)
        print('')

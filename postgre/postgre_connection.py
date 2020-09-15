import psycopg2
from sqlalchemy import create_engine

import json

class connect_to_postgre:
    def __init__(self,config_file):
        self.config_file=config_file

    def read_config_file(self):
        with open(self.config_file,'r') as json_file:
            self.config=json.load(json_file)

    def connect_to_db(self):
        # read conf file
        self.read_config_file()
        # connect to db
        user=self.config['PostgreSQL']['username']
        database=self.config['PostgreSQL']['dbName']
        password=self.config['PostgreSQL']['password']
        host=self.config['PostgreSQL']['host']
        port=self.config['PostgreSQL']['port']
        self.engine=create_engine("postgresql+psycopg2://{}:{}@{}:{}/{}".format(user,password,host,port,database))
        # get tables and test the connection
        query="""SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE';
        """
        tables=self.engine.execute(query).fetchall()
        self.tables=[tabl[0] for tabl in tables]
        print('Connected to PostgreSQL')
        print('Current tables:',self.tables)
        print('')

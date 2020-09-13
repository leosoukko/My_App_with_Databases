import psycopg2

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
        self.conn=psycopg2.connect(database=self.config['PostgreSQL']['dbName'],
                                    user=self.config['PostgreSQL']['username'],
                                    password=self.config['PostgreSQL']['password'])
        #print some info
        cur = self.conn.cursor()
        print('Connected to',self.config['PostgreSQL']['dbName'])
        query="""SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE';
        """
        cur.execute(query)
        # display the PostgreSQL database server version
        result = cur.fetchone()
        print('Current tables:',result)
        cur.close()

psql=connect_to_postgre('database_config.json')
psql.connect_to_db()
        
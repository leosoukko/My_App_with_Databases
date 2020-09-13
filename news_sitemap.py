# my files
import mongodb_connection
# already with python
import re
from collections import Counter
import datetime
# need to install
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
print('')

class get_sitemap_data:
    def __init__(self,URL,removableWords,tag,db_config_file):
        # for db connection
        self.db_config_file=db_config_file
        # the url of recent news sitemap xml
        self.url=URL
        # mongo db collection name
        self.collection_name=self.url.split('/')[2].split('.')[1]
        # removable words
        self.removableWords=Counter(removableWords)
        self.stopwords_dict = Counter(stopwords.words())#counter makes the script 100 times faster, it is crazy
        # not all sitemaps have identical tags
        self.tag=tag

    def connect_to_db(self):
        self.mongodb_connection=mongodb_connection.connect_to_mongodb(self.db_config_file)
        self.mongodb_connection.connect_to_db()
        print('Database collection count when connecting:',self.mongodb_connection.db[self.collection_name].count())

    # get articles on the sitemap xml
    def get_articles(self):
        self.site=requests.get(self.url)
        if self.site.ok:
            self.soup=bs(self.site.text,'html.parser')
            self.articles=self.soup.find_all('url')
            print('Fetched xml')
        else:
            print('Failed to fetch xml')
            exit()

    # parse text
    def parse_text(self,text):
        text=text.lower().replace(' ','_').replace('-','_').replace('&apos;','')
        text=re.sub('\W','',text)#get rid of whitespaces
        text=re.sub('\d','',text)#get rid of digits
        words=text.split('_')
        words=[word for word in words if word not in self.removableWords]#get rid of removable words
        words = [word for word in words if word not in self.stopwords_dict]#get rid of stopwords
        words = list(filter(None, words))#get rid of '' elements
        return words

    # get stock market tickers if available
    def get_tickers(self,article):
        tickers=article.find('{}:stock_tickers'.format(self.tag))
        if tickers!=None:
            tickers=tickers.getText().lower().replace(' ','').replace('_',':')
            tickers=tickers.split(',')
        else:
            tickers=['']
        return tickers
    
    def check_if_already_exists(self,link):
        link_exists=self.mongodb_connection.db[self.collection_name].count_documents({"link":link})
        # if the link does not exist, return true
        if link_exists==0:
            return True
        else:
            return False

    def update_data(self,date,link,title,tickers):
        self.mongodb_connection.db[self.collection_name].insert_one({"date":date,"link":link,"title":title,"tickers":tickers})

    def get_and_update_data(self):
        # connect to the database
        self.connect_to_db()
        # get all articles in the sitemap
        self.get_articles()
        # for each article
        for i,article in enumerate(self.articles):
            # print every 100 iterations
            if (i+1)%100==0:
                print('Article',i+1,'/',len(self.articles),'being processed')
            #get link
            link=article.find('loc').getText()
            new_data=self.check_if_already_exists(link)
            if new_data:
                # get date
                date=article.find('{}:publication_date'.format(self.tag)).getText().replace("Z", "+00:00")
                date=datetime.datetime.fromisoformat(date)
                #get stock tickers
                tickers=self.get_tickers(article)
                # get title
                try:
                    title=article.find('{}:title'.format(self.tag)).getText()
                    title=self.parse_text(title)
                except:
                    title=['']

                self.update_data(date,link,title,tickers)

        print('Database collection count after connecting:',self.mongodb_connection.db[self.collection_name].count())

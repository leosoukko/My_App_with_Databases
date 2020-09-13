# already with python
import re
from collections import Counter
# need to install
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
print('')

class get_sitemap_data:
    def __init__(self,URL,removableWords,tag):
        # the url of recent news sitemap xml
        self.url=URL
        self.site=requests.get(URL)
        self.removableWords=Counter(removableWords)
        self.stopwords_dict = Counter(stopwords.words())#counter makes the script 1000 times faster, it is crazy
        self.tag=tag# not all sitemaps have identical tags
        self.output={}

    # get articles on the sitemap xml
    def get_articles(self):
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

    def get_data(self):
        # get all articles in the sitemap
        self.get_articles()
        # for each article
        for i,article in enumerate(self.articles):
            #get stock tickers
            tickers=self.get_tickers(article)
            #get link
            link=article.find('loc').getText()
            # get title
            try:
                title=article.find('{}:title'.format(self.tag)).getText()
                title=self.parse_text(title)
            except:
                title=['']
            # get keywords
            try:
                keywords=article.find('{}:keywords'.format(self.tag)).getText().lower().replace(' ','').split(',')
                keywords = list(filter(None, keywords))
            except:
                keywords=['']
            # get date
            date=article.find('{}:publication_date'.format(self.tag)).getText()

            #save outputs, need to have unique index
            IndeX=self.url+'_'+str(i)
            self.output[IndeX]={}
            self.output[IndeX]['date']=date
            self.output[IndeX]['link']=link
            self.output[IndeX]['title']=title
            self.output[IndeX]['tickers']=tickers
            self.output[IndeX]['keywords']=keywords
            # print every 100 iterations
            if (i+1)%100==0:
                print('Article',i+1,'/',len(self.articles),'processed')

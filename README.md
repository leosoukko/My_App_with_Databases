This repo is my test to use MongoDB and PostgreSQL with Python.

### Prerequirements

Install MongoDB and PostgreSQL.
Install requirements.txt packages.

Create a "config" folder and a "database_config.json" file in it. This file has all the configurations needed to connect to the databases. It currently as:
{
    "MongoDB":{"URI":"some_value"},
    "PostgreSQL":{"dbName":"some_value","username":"some_value","password":"some_value","host":"some_value","port":"some_value"}
}

### File Descriptions

**postgre folder**
- This folder has three files:
    - postgre_connection.py
        - Connects to postgresql database with credentials given in config/database_config.json
    - london_stocks.txt
        - Names of all stocks that one wants to fetch
    - london_stock_data.py
        - Uses postgre_connection.py to connect to the database.
        - Fetches trades done for current day for all stocks in london_stocks.txt file from London Stock Exchange API. If a stock does not have its own table in the database then the script creates one. Adds only newer data than those that already exists in the table. Sleeps 6-10 secs between the API calls.

**mongo folder**
- This folder has four files:
    - mongodb_connection.py
        - Connects to MongoDB database with URI given in config/database_config.json
    - sitemaps.txt
        - Has URLS of all sitemaps one wants to fetch.
    - news_sitemap.py
        - Fetches one sitemap.xml file and parses information of title, tickers, publication time
This repo fetches sitemap news from Reuters, Financial Times and MarketWatch and adds all new article links, titles, tickers and dates to mongodb database. Each site has their own collection of objects. One needs to have MongoDB installed to use the repo.

**File Descriptions**

database_config.json
- Currently has only URI for the MongoDB database.

sitemaps.txt
- List of sitemap xml urls to fetch

mongodb_conncetion.py
- Establishes MongoDB conncetion using database_config.json

news_sitemap.py
- Fetches news from a given sitemap xml file. Inserts all new articles to the database to correct collection.
- Uses mongodb_connection.py

controller.py
- Reads sitemap.txt file and then uses news_sitemap.py for each sitemap url.
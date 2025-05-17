# CN230 Project: Danbooru

    python dbr_cn230.py

# Requirements
1. Pandas (pandas - Python Data Analysis Library)
2. Matplot Library (Matplotlib — Visualization with Python)
3. SQLite3 (sqlite3 — DB-API 2.0 interface for SQLite databases)
4. Danbooru API Keys (will not be provided obviously)
```
pip install pandas matplotlib sqlite3
```
# Details
Utilizing Danbooru's own API to fetch the artist and copyright tags from the website then do data analytics based on that.  
Fetch 1,000 artists and 100 copyright tags by default.  
An example database (.db) file is provided in case if you don't have access to the API, and the data is filtered to only display tags after the year 2014 due to the limitations of the API (see sources for more info).  

Matplot Library and Pandas is used for data visualization and to stylize to make data look more visually appealing and more readable.  

# Sources
Danbooru Public APIs: https://danbooru.donmai.us/wiki_pages/help:api

API Keys can be acquired by creating a Danbooru account.

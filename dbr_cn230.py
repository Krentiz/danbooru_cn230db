import requests
import json
import sqlite3

import pandas as pd
import matplotlib.pyplot as plt

url = "https://danbooru.donmai.us/tags.json"
query = "?search[order]=count&search[hide_empty]=yes"
user = "USER"
apikey = "API_KEY"


def fetch_and_insert(
    db_name: str, table_name: str, url: str, query: str, user: str, apikey: str
):
    response = requests.get(url + query, auth=(user, apikey))
    if response.status_code in range(200, 300):
        data = json.loads(response.text)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS """
            + table_name
            + """ (
            id INTEGER PRIMARY KEY,
            name TEXT,
            post_count INTEGER,
            created_at STRING,
            updated_at STRING
        )
        """
        )

        for item in data:
            cursor.execute(
                """
                INSERT OR REPLACE INTO """
                + table_name
                + """ (id, name, post_count, created_at, updated_at) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    item["id"],
                    item["name"],
                    item["post_count"],
                    item["created_at"],
                    item["updated_at"],
                ),
            )

        conn.commit()
        conn.close()

        print(table_name + " data inserted into sqlite (" + db_name + ") database.")
    else:
        raise Exception(response.status_code)


ans_box = input(
    "Execution Mode:"
    "\nY: Fetch and Run, N: Run only (using the provided tags.db)"
    "\nPlease choose Run only if you don't have access to API Key >>> "
)

if ans_box.capitalize() == "Y":

    print()

    # fetch copyright (titles) with a sample size of 100 titles
    fetch_and_insert(
        "tags.db",
        "copyright",
        url,
        query + "&search[category]=1&limit=100",
        user,
        apikey,
    )

    # fetch artist with a sample size of 1000 artists
    fetch_and_insert(
        "tags.db", "artist", url, query + "&search[category]=3&limit=1000", user, apikey
    )

elif ans_box.capitalize() != "N":

    print()

    raise Exception("Invalid response.")

# assuming everything above is said and done

print()

db_path = "tags.db"
conn = sqlite3.connect(db_path)

copyright_full = pd.read_sql_query(
    "SELECT name, post_count, created_at FROM copyright", conn
)
artist_full = pd.read_sql_query("SELECT name, post_count, created_at FROM artist", conn)

tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql_query(tables_query, conn)


### basic stuffs
top_artists = pd.read_sql_query(
    """
    SELECT name, post_count FROM copyright
    ORDER BY post_count DESC
    LIMIT 10
""",
    conn,
)
top_copyrights = pd.read_sql_query(
    """
    SELECT name, post_count FROM artist
    ORDER BY post_count DESC
    LIMIT 10
""",
    conn,
)
latest_artist_update = pd.read_sql_query(
    """
    SELECT name, updated_at FROM copyright
    ORDER BY updated_at DESC
    LIMIT 5
""",
    conn,
)
latest_copyright_update = pd.read_sql_query(
    """
    SELECT name, updated_at FROM artist
    ORDER BY updated_at DESC
    LIMIT 5
""",
    conn,
)

print("Top 10 Artists by Post Count:")
print(top_artists)
print()

print("Top 10 Copyright titles by Post Count:")
print(top_copyrights)
print()

print("Most Recently Updated Artists:")
print(latest_artist_update)
print()

print("Most Recently Updated Tags:")
print(latest_copyright_update)
print()

### percentiles stuffs
artist_percentiles = artist_full["post_count"].quantile(
    [0.01, 0.25, 0.5, 0.75, 0.95, 0.99]
)
copyright_percentiles = copyright_full["post_count"].quantile(
    [0.01, 0.25, 0.5, 0.75, 0.95, 0.99]
)

# extract rare and top tags/artists
rare_tags = artist_full[
    artist_full["post_count"] <= artist_percentiles[0.01]
].sort_values(by="post_count")
top_tags = artist_full[
    artist_full["post_count"] >= artist_percentiles[0.99]
].sort_values(by="post_count", ascending=False)

rare_artists = copyright_full[
    copyright_full["post_count"] <= copyright_percentiles[0.01]
].sort_values(by="post_count")
top_artists = copyright_full[
    copyright_full["post_count"] >= copyright_percentiles[0.99]
].sort_values(by="post_count", ascending=False)

print("Artists top percentiles:")
print(artist_percentiles)
print()

print("Copyright titles top percentiles:")
print(copyright_percentiles)
print()

print("Top Artists (from the top 1%, first 5 entries)")
print(top_artists.head(5))
print()

print("Top Copyright titles (from the top 1%, first 5 entries)")
print(top_copyrights.head(5))
print()

print("Rare Artists (from the bottom 1%, first 5 entries)")
print(rare_artists.head(5))
print()

print("Rare Copyright titles (from the bottom 1%, first 5 entries)")
print(rare_tags.head(5))
print()


### histogram stuffs
# convert created_at to datetime with UTC handling
copyright_full["created_at"] = pd.to_datetime(
    copyright_full["created_at"], errors="coerce", utc=True
)
artist_full["created_at"] = pd.to_datetime(
    artist_full["created_at"], errors="coerce", utc=True
)

# filter outliers for visualization
filtered_artist = artist_full[artist_full["post_count"] < 20000]
filtered_copyright = copyright_full[copyright_full["post_count"] < 10000]

# plot histogram
plt.figure(figsize=(12, 6))
plt.hist(
    filtered_artist["post_count"],
    bins=50,
    alpha=0.6,
    label="Tags (Artist Table)",
    color="orange",
)
plt.hist(
    filtered_copyright["post_count"],
    bins=50,
    alpha=0.6,
    label="Artists (Copyright Table)",
    color="blue",
)

plt.title("Distribution of Post Counts (Filtered)")
plt.xlabel("Post Count")
plt.ylabel("Number of Tags/Artists")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

### time-based trend analysis
# group by creation year and sum post countss
copyright_trend = (
    copyright_full.dropna(subset=["created_at"])
    .groupby(copyright_full["created_at"].dt.tz_localize(None).dt.to_period("Y"))[
        "post_count"
    ]
    .sum()
    .reset_index()
)
copyright_trend["created_at"] = copyright_trend["created_at"].dt.to_timestamp()

artist_trend = (
    artist_full.dropna(subset=["created_at"])
    .groupby(artist_full["created_at"].dt.tz_localize(None).dt.to_period("Y"))[
        "post_count"
    ]
    .sum()
    .reset_index()
)
artist_trend["created_at"] = artist_trend["created_at"].dt.to_timestamp()

# filter data before 2014 (due to the api restrictions)
copyright_trend = copyright_trend[copyright_trend["created_at"].dt.year >= 2014]
artist_trend = artist_trend[artist_trend["created_at"].dt.year >= 2014]

# plot time-based trends
plt.figure(figsize=(12, 6))
plt.plot(
    copyright_trend["created_at"],
    copyright_trend["post_count"],
    label="Copyright (Artist) Post Count",
    marker="o",
)

plt.plot(
    artist_trend["created_at"],
    artist_trend["post_count"],
    label="Tag (Artist) Post Count",
    marker="o",
    color="darkorange",
)

plt.title("Post Count Growth Over Time")
plt.xlabel("Year")
plt.ylabel("Total Post Count")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

conn.close()

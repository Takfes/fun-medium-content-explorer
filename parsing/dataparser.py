import json
import os
import pickle
import time
from pathlib import Path
from typing import Dict

from bs4 import BeautifulSoup
from newspaper import Article
from tqdm import tqdm

from crawling.config import FOLDER_BRONZE, FOLDER_GOLD, FOLDER_SILVER


def auto_parse_html(soup: BeautifulSoup) -> Dict:
    obj = {}
    # Create an Article object
    article = Article("")
    # Set the HTML content
    html_content = str(soup)
    article.set_html(html_content)
    # Parse the article
    article.parse()
    # You can now access various properties of the article, such as:
    obj["title"] = article.title
    obj["authors"] = article.authors
    obj["publish_date"] = article.publish_date.strftime("%Y-%m-%d %H:%M:%S")
    obj["keywords"] = article.keywords
    obj["summary"] = article.summary
    obj["top_image"] = article.top_image
    obj["tags"] = list(article.tags)
    obj["images"] = list(article.images)
    obj["text"] = article.text
    return obj


# ===============================================
# Merge all bronze items into a single file, master.
# master = {mediumid : {}, mediumid : {}}
# ===============================================

readpath = Path(FOLDER_BRONZE)
bronzefiles = list(readpath.glob("*.json"))
master = {}

for bf in bronzefiles:
    with open(bf, "r", encoding="utf-8") as file:
        collection = json.load(file)
        for c in collection:
            try:
                master[c.get("mediumid")] = c
            except Exception as e:
                print(f"{bf.stem}")
                print(c)

print(f"Created master with {len(master.keys())} items")

# ===============================================
# Iterate through master items
# For each master item, search in silver based on key <key>.html
# then parse <k>.html and append/update info to master like so:
# master = {mediumid : {... + parsed info}, mediumid : {... + parsed info}}
# ===============================================

counter = 1
fails = []

start = time.perf_counter()

for k, v in master.items():
    temp_path = f"{FOLDER_SILVER}/{k}.html"

    if not os.path.exists(temp_path):
        continue

    try:
        with open(temp_path, "r", encoding="utf-8") as file:
            html = file.read()
            parsed_html = auto_parse_html(html)

        del parsed_html["title"]
        del parsed_html["authors"]
        del parsed_html["publish_date"]
        master.get(k).update(parsed_html)
        print(f"Parsed item ({counter}/{len(master.keys())}): {k}")
        counter += 1

    except Exception as e:
        fails.append(k)
        print(f"Failed to parse html content for {k}")
        print(f"Running fails {len(fails)}")

end = time.perf_counter()

print(f"Parsed {counter} in {end-start:.4f} seconds")
print(f"Failed to parse {len(fails)=} items")

# ===============================================
# Write final object to disk
# ===============================================

with open(f"{FOLDER_GOLD}/master.json", "wb") as m:
    pickle.dump(master, m)

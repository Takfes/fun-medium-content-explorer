import json
import os
import pickle
import re
import time
from pathlib import Path
from typing import Dict

from bs4 import BeautifulSoup
from newspaper import Article
from tqdm import tqdm

from config import FOLDER_BRONZE, FOLDER_GOLD, FOLDER_SILVER


def clean_text(text, to_lower=False):
    # Replace newline characters with a space
    text = text.replace("\n", " ")
    # Replace multiple consecutive whitespaces with a single space
    text = re.sub(r"\s+", " ", text)
    # Strip leading and trailing whitespace
    text = text.strip()
    # Optionally, convert to lowercase
    if to_lower:
        text = text.lower()
    return text


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
    # obj["title"] = article.title
    # obj["authors"] = article.authors
    # obj["publish_date"] = article.publish_date.strftime("%Y-%m-%d %H:%M:%S")
    # obj["keywords"] = article.keywords
    # obj["summary"] = article.summary
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

print(50 * "=")
print(f"\nConsolidating bronze data into a single master file...")

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

print(50 * "=")
print(f"\nParsing silver data in the master file from above...")

for k, v in master.items():
    temp_path = f"{FOLDER_SILVER}/{k}.html"

    if not os.path.exists(temp_path):
        continue

    try:
        with open(temp_path, "r", encoding="utf-8") as file:
            html = file.read()
            parsed_html = auto_parse_html(html)

        # delete key 'is_series' before adding to master data
        del master[k]["is_series"]
        # clean text before adding to master data
        parsed_html["text"] = clean_text(parsed_html["text"])
        # update master data for item k with parsed_html keys
        master.get(k).update(parsed_html)
        print(f"Parsed item ({counter}/{len(master.keys())}): {k}")
        counter += 1

    except Exception as e:
        fails.append(k)
        # delete the item if its html couldn't be parsed
        del master[k]
        print(f"Failed to parse html content for {k}")
        print(f"Running fails {len(fails)}")

end = time.perf_counter()

print(f"Parsed {counter} in {end-start:.4f} seconds")
print(f"Failed to parse {len(fails)=} items")

# ===============================================
# Write final object to disk
# ===============================================

with open(f"{FOLDER_GOLD}/master.pickle", "wb") as m:
    pickle.dump(master, m)

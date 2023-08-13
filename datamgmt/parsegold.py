import json
import os
import pickle
import re
import time
from pathlib import Path
from typing import Dict

from bs4 import BeautifulSoup
from newspaper import Article

from config import FOLDER_ALERTS, FOLDER_BRONZE, FOLDER_GOLD, FOLDER_SILVER


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
# Iterate through master items
# For each master item, search in silver based on key <key>.html
# then parse <k>.html and append/update info to master like so:
# master = {mediumid : {... + parsed info}, mediumid : {... + parsed info}}
# ===============================================

bronzepath = Path(FOLDER_BRONZE)
bronzefile = list(bronzepath.iterdir())[0]
with open(bronzefile, "r", encoding="utf-8") as file:
    master = json.load(file)

counter = 1
failed = []
missing = []

start = time.perf_counter()

print(50 * "=")
print(f"\nParsing silver data in the master file from above...")

for k, v in master.items():
    temp_path = f"{FOLDER_SILVER}/{k}.html"

    if not os.path.exists(temp_path):
        missing.append(temp_path)
        continue

    try:
        with open(temp_path, "r", encoding="utf-8") as file:
            html = file.read()
            parsed_html = auto_parse_html(html)

        # clean text before adding to master data
        parsed_html["text"] = clean_text(parsed_html["text"])
        # update master data for item k with parsed_html keys
        # update items based on the auto_parse_html function :
        # tog_image, images, tags, text
        master.get(k).update(parsed_html)
        print(f"Parsed item ({counter}/{len(master.keys())}): {k}")
        counter += 1

    except Exception as e:
        failed.append(k)
        # delete the item if its html couldn't be parsed
        del master[k]
        print(f"Failed to parse html content for {k}")
        print(f"Running failed {len(failed)}")

end = time.perf_counter()

print(f"Parsed {counter} in {end-start:.4f} seconds")
print(f"Failed to parse {len(failed)=} items")
print(f"Detected {len(missing)=} missing files")

# ===============================================
# Write final object to disk
# Write missing and failed to disk
# ===============================================

with open(f"{FOLDER_GOLD}/master.pickle", "wb") as m:
    pickle.dump(master, m)

with open(f"{FOLDER_ALERTS}/missing.pickle", "wb") as m:
    pickle.dump(missing, m)

with open(f"{FOLDER_ALERTS}/failed.pickle", "wb") as m:
    pickle.dump(failed, m)

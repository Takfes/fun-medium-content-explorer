import datetime
import json
from pathlib import Path
from typing import Dict

from bs4 import BeautifulSoup
from newspaper import Article

from parsing.config import FOLDER_GOLD, FOLDER_SILVER


def auto_parse_html(mid: str, soup: BeautifulSoup) -> Dict:
    obj = {}
    # Create an Article object
    article = Article("")
    # Set the HTML content
    html_content = str(soup)
    article.set_html(html_content)
    # Parse the article
    article.parse()
    # You can now access various properties of the article, such as:
    obj["id"] = mid
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


readpath = Path(FOLDER_SILVER)
readfiles = list(readpath.glob("*.html"))
html_data = []

for f in readfiles:
    with open(f, "r", encoding="utf-8") as file:
        html_content = file.read()
        parsed_item = auto_parse_html(f.stem, html_content)
        with open(f"{FOLDER_GOLD}/{f.stem}.json", "w", encoding="utf-8") as jf:
            json.dump(parsed_item, jf)

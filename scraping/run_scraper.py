
from scraping.config import COLLECTIONS, DATA_FOLDER
from scraping.myio import dump_to_path
from scraping.main import scraper

LIMIT = 50

if __name__ == "__main__":
    try:
        for k, v in COLLECTIONS.items():
            items = scraper(k, LIMIT)
            dump_to_path(items, f"{DATA_FOLDER}/{k}")
    except Exception as e:
        print(f"{e}")

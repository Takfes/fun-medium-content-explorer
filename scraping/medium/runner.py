import importlib

from scraping.medium.config import COLLECTIONS, DATA_FOLDER
from scraping.myio import dump_to_path

module = "medium"
limit = 50

if __name__ == "__main__":
    try:
        scraper = importlib.import_module(f"scraping.{module}.main")
        entry_point = getattr(scraper, "default")
        for k, v in COLLECTIONS.items():
            items = entry_point([k, 50])
            dump_to_path(items, f"{DATA_FOLDER}/{k}")
    except ModuleNotFoundError:
        print(f"module '{module}' not found!")

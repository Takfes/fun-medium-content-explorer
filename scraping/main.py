import importlib
import sys


def default():
    module = sys.argv[1]
    try:
        scraper = importlib.import_module(f"scraping.{module}.main")
        entry_point = getattr(scraper, "default")
        entry_point(sys.argv[2:])
    except ModuleNotFoundError:
        print(f"module '{module}' not found!")

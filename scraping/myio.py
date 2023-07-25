import datetime
import json
from pathlib import Path


def dump_to_path(items, filepath):
    timetag = datetime.datetime.now().strftime("%Y%m%d|%H%M%S")
    filepath = Path(f"{filepath}|{timetag}")
    with open(f"{filepath}.json", mode="w", encoding="utf-8") as f:
        json.dump(items, f)

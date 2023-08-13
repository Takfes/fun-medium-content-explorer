import datetime
import json
from pathlib import Path

from config import FOLDER_BRONZE, FOLDER_RAW, FOLDER_SILVER, FOLDER_STAGE

# ===============================================
# parse raw data coming from scraper medium requests
# ===============================================

rawpath = Path(FOLDER_RAW)

counter = 0
data = {}  # TODO implement a custom dataclass

# iterate through raw files
for path in rawpath.iterdir():
    user_collection = path.stem.split("|")[0]

    # don't parse the reading_list collection
    if user_collection == "reading_list":
        continue

    # for any other collection, open its collection_list
    with open(path, "r", encoding="utf-8") as f:
        collection_list = json.load(f)

    # iterate across items from collection list
    # discard empty items which seem to exist
    # scope is to create a consolidated data structure to hold all items
    # if an item appears in more than one list, ...
    # ... update its user_collection attribute with the different lists that is part of
    for i, item in enumerate(collection_list):
        if not item:  # discard empty items which seem to exist
            continue

        counter += 1

        if not item["id"] in set(data.keys()):
            item["user_collection"] = [user_collection]
            data[item["id"]] = item

        elif item["id"] in set(data.keys()):
            existing_item = data[item["id"]]
            data[item["id"]]["user_collection"].append(user_collection)

print(f"Iterate over {counter} raw items\nFound {len(set(data.keys()))} unique items")

# ===============================================
# Add parsed|consolidated raw files to bronze folder
# ===============================================

bronzepath = Path(FOLDER_BRONZE)

with open(f"{bronzepath}/itemswdis.json", "w", encoding="utf-8") as file:
    json.dump(data, file)

# ===============================================
# Compare with silver to find files for which need to obtain their html and put in silver folder
# ===============================================

# ids derived from raw folder
data_ids = set(data.keys())

# ids from silver folder - i.e. items whose htmls already exist
silverpath = Path(FOLDER_SILVER)
silver_file_ids = {x.stem for x in list(silverpath.iterdir())}

# find the files whose htmls are missing
newfiles_ids = data_ids.difference(silver_file_ids)

# put these files to staging - files that need parsing
stagepath = Path(FOLDER_STAGE)
stagepath_timetag = datetime.datetime.now().strftime("%Y%m%d|%H%M%S")
stage_files = [data[x] for x in newfiles_ids]

print(f"Identified {len(stage_files)} items with no html files\nAdding to {stagepath}")

with open(f"{stagepath}/staged{stagepath_timetag}.json", "w", encoding="utf-8") as file:
    json.dump(stage_files, file)

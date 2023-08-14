import datetime
import json
from pathlib import Path

from config import FOLDER_BRONZE, FOLDER_RAW, FOLDER_SILVER, FOLDER_STAGE

# ===============================================
# parse raw data coming from scraper medium requests
# ===============================================

rawpath = Path(FOLDER_RAW)

cum_cntr = 0
cum_list = 0
data = {}  # TODO implement a custom dataclass

# iterate through raw files
for path in rawpath.iterdir():
    pile = path.stem.split("|")[0]

    # don't parse the reading_list collection
    if pile == "reading_list":
        path.unlink()
        continue

    counter = 0
    # for any other collection, open its collection_list
    with open(path, "r", encoding="utf-8") as f:
        collection_list = json.load(f)

    cum_list += len(collection_list)

    # iterate across items from collection list
    # discard empty items which seem to exist
    # scope is to create a consolidated data structure to hold all items
    # if an item appears in more than one list, ...
    # ... update its pile attribute with the different lists that is part of
    for i, item in enumerate(collection_list):
        if not item:  # discard empty items which seem to exist
            continue

        counter += 1

        if not item["id"] in set(data.keys()):
            item["pile"] = [pile]
            data[item["id"]] = item

        elif item["id"] in set(data.keys()):
            existing_item = data[item["id"]]
            data[item["id"]]["pile"].append(pile)

    print(
        f"* Collection {pile} | {counter}/{len(collection_list)} - ({counter/len(collection_list):.1%})"
    )
    cum_cntr += counter
    path.unlink()

print(f"Iterate over {cum_cntr} raw items\nFound {len(set(data.keys()))} unique items")

# ===============================================
# Add parsed|consolidated raw files to bronze folder
# ===============================================

bronzepath = Path(FOLDER_BRONZE)

with open(f"{bronzepath}/bronzemaster.json", "w", encoding="utf-8") as file:
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

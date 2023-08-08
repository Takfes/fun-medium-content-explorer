import json
import time
from pathlib import Path

import redis
from tqdm import tqdm

from redisdb.config import READ_FOLDER


def load_from_path(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


# ===============================================
# Connect to Redis
# ===============================================
r = redis.Redis(host="localhost", port=6379, db=0)

# ===============================================
# Read data and push to Redis
# ===============================================

mapping = {}
collections = {}
counter_list = 0
data = []
fail = []

readpath = Path(READ_FOLDER)
readfiles = list(readpath.glob("*.json"))

for f in readfiles:
    items = load_from_path(f)
    print(f"{f.stem} : {len(items)} items")
    collections[f.stem] = len(items)
    for item in tqdm(items):
        try:
            mid, url = item.get("mediumid"), item.get("medium_url")
            mapping[mid] = url
            data.append(dict(id=mid, url=url, topic=f.stem))
            counter_list += 1
        except Exception as e:
            print(e)
            fail.append(item)

assert len(data) == counter_list

with open("data/map.json", "w") as file:
    json.dump(mapping, file)

# ===============================================
# Push data to REDIS
# ===============================================

start = time.perf_counter()
counter_redis = 0

for d in data:
    print(f"Pushing {d.get('id')} to REDIS")
    # Convert the dictionary to a JSON string to store in Redis
    data_json = json.dumps(d)
    # Push the JSON string to the end of the list (the "queue")
    r.rpush("queue", data_json)
    counter_redis += 1

end = time.perf_counter()
print(f"Pushed {counter_redis} items in {end-start:.4f}")

# ===============================================
# Validate all items stored in REDIS
# ===============================================

redis_items = r.lrange("queue", 0, -1)
assert counter_redis == len(redis_items)
print(f"{counter_redis=} stored in REDIS")
print(f"{counter_redis=} stored in REDIS")

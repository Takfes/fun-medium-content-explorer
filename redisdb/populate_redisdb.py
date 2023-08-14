import json
import time
from pathlib import Path

import redis

from config import FOLDER_STAGE, REDIS_HOST, REDIS_MAIN_QUEUE

# ===============================================
# Connect to Redis
# ===============================================
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

# ===============================================
# Push data to REDIS
# ===============================================

stagepath = Path(FOLDER_STAGE)
counter = 0

start = time.perf_counter()

for f in stagepath.iterdir():
    with open(f, "r") as file:
        data = json.load(file)

    # Push items to the queue
    for item in data:
        truncated_item = {}
        truncated_item["id"] = item["id"]
        truncated_item["url"] = item["url"]
        message = json.dumps(truncated_item)
        r.rpush(REDIS_MAIN_QUEUE, message)

    print(f"* items {f} sent to the queue")
    print(f"* deleting items {f}\n")
    counter += len(data)
    f.unlink()

end = time.perf_counter()
print(f"Pushed {counter} items in {end-start:.4f}")

# ===============================================
# Validate all items stored in REDIS
# ===============================================

redis_items = r.lrange(REDIS_MAIN_QUEUE, 0, -1)
assert counter == len(redis_items)
r.close()

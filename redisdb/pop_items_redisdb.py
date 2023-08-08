import json

import redis

# ===============================================
# Connect to Redis
# ===============================================
r = redis.Redis(host="localhost", port=6379, db=0)

# ===============================================
# How to pop items from REDIS to process them
# ===============================================

counter_jobs = 0

while True:
    current_job = r.rpop("queue")
    if current_job:
        current_job = json.loads(current_job)
        print(f"Visiting: {current_job}")
        counter_jobs += 1
    else:
        print(50 * "=")
        print(f"Visited {counter_jobs} items! Done visiting")
        break

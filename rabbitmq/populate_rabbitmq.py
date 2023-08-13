import json
from pathlib import Path

import pika

from config import FOLDER_STAGE, RABBITMQ_HOST, RABBITMQ_MAIN_QUEUE
from secretkeys import RABBITMQ_PASS, RABBITMQ_USER

# Define RabbitMQ credentials
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
# Connect to RabbitMQ with credentials
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
)
channel = connection.channel()
# Declare a queue
queue = channel.queue_declare(queue=RABBITMQ_MAIN_QUEUE)


stagepath = Path(FOLDER_STAGE)
counter = 0

# Read JSON file
for f in stagepath.iterdir():
    with open(f, "r") as file:
        data = json.load(file)

    # Push items to the queue
    for item in data:
        truncated_item = {}
        truncated_item["id"] = item["id"]
        truncated_item["url"] = item["url"]
        message = json.dumps(truncated_item)
        channel.basic_publish(exchange="", routing_key=RABBITMQ_MAIN_QUEUE, body=message)

    print(f"* items {f} sent to the queue")
    print(f"* deleting items {f}\n")
    counter += len(data)
    # f.unlink()

print(f"Send a total of {counter} messaged to {RABBITMQ_HOST}.{RABBITMQ_MAIN_QUEUE}")

# ===============================================
# Validate all items stored in RABBITMQ
# ===============================================

message_count = queue.method.message_count
assert counter == message_count
connection.close()

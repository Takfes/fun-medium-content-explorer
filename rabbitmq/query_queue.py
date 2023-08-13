import pika

from config import RABBITMQ_HOST, RABBITMQ_MAIN_QUEUE
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
message_count = queue.method.message_count
print(f"There are {message_count} messages in the queue")

connection.close()

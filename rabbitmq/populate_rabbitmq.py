import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
queue_name = "my_queue"
channel.queue_declare(queue=queue_name)

# Publish a message to the queue
channel.basic_publish(exchange="", routing_key=queue_name, body="Hello World!")
print("Sent 'Hello World!'")

# check queue size
queue = channel.queue_declare(queue=queue_name, passive=True)
queue_size = queue.method.message_count
print(f"Queue size: {queue_size}")

# close connection
connection.close()

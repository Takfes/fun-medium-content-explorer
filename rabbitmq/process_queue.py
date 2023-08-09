import pika


def callback(ch, method, properties, body):
    print(f"Received {body}")
    try:
        # Process the message here
        # If successful, send acknowledgment
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Failed to process message: {e}")
        # If processing fails, you can reject the message and requeue it
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)


# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

# Declare the queue (make sure it matches the name of the queue you're using)
queue_name = "my_queue"
channel.queue_declare(queue=queue_name)

# Set the quality of service to process one message at a time
channel.basic_qos(prefetch_count=1)

# Start consuming messages from the queue
channel.basic_consume(queue=queue_name, on_message_callback=callback)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
channel.start_consuming()

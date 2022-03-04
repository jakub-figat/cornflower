import json

import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        port=5672,
        credentials=pika.PlainCredentials(username="rabbitmquser", password="somepassword"),
    )
)

channel = connection.channel()

channel.queue_declare(queue="user.register", durable=True)

body = {"user": "macko z klanu, brak browaru"}

channel.basic_publish(exchange="", routing_key="user.register", body=json.dumps(body).encode("utf-8"))

print("MESSAGE SENT!")

connection.close()

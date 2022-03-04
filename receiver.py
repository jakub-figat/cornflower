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


def callback(channel, method, properties, body):
    print(f"Message is: {body.decode('utf-8')}")


channel.basic_consume(queue="user.register", on_message_callback=callback, auto_ack=True)

channel.start_consuming()

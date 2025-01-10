import json

from common.message import NotificationMessage
from pika import BasicProperties, BlockingConnection  # type: ignore

from kit.mqx import RabbitMQConfig


class MessageSender:
    def __init__(self, config: RabbitMQConfig):
        # Establish connection to RabbitMQ
        self.mq_connection = BlockingConnection(config.get_connection_params())

    def send_message(self, message: NotificationMessage):
        channel = self.mq_connection.channel()

        # Declare the same queue as the worker to ensure it exists
        channel.queue_declare(queue="notification", durable=True)

        # Convert the message to a JSON string
        message_body = json.dumps(message.__dict__)

        # Publish the message to the queue
        channel.basic_publish(
            exchange="",
            routing_key="notification",
            body=message_body,
            properties=BasicProperties(
                delivery_mode=2  # Make message persistent
            ),
        )

        print(f" [x] Sent {message_body}")
        channel.close()

    def close(self):
        # Ensure the connection and channel are closed properly
        self.mq_connection.close()

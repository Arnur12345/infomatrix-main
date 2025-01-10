import argparse
import json
import os
from datetime import datetime

import cv2
from common.message import NotificationMessage
from common.models import EventType
from pika import BasicProperties, BlockingConnection  # type: ignore

from notification_app.notification_worker.config import Config, read_config


def send_message(mq_connection: BlockingConnection, message: NotificationMessage):
    channel = mq_connection.channel()

    # Declare the same queue as the worker to ensure it exists
    channel.queue_declare(queue="notification", durable=True)

    # Convert the message to a JSON string
    message.org_id = "99093da9-8a6c-456d-9a17-4f8cd2101b92"
    message.main_actor_id = "e2049454-f505-4272-9857-834b28414321"
    message.event_type = EventType.STUDENT_ENTRANCE
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


def sender():
    parser = argparse.ArgumentParser(
        prog="send notification",
        description="sends a notification message to the queue",
    )
    parser.add_argument(
        "--config_path",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "config.yaml"),
        help="path to the configuration file",
    )
    args = parser.parse_args()

    # Load the configuration
    config = read_config(args.config_path)
    image = cv2.imread("image_examples/biden.jpg")
    from kit.utils import cv_image_to_base64

    # Create the notification message object
    notification_message = NotificationMessage(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), image=cv_image_to_base64(image)
    )

    # Establish connection to RabbitMQ
    mq_connection = BlockingConnection(config.message_queue.get_connection_params())

    # Send the message
    send_message(mq_connection, notification_message)

    # Close the connection
    mq_connection.close()


if __name__ == "__main__":
    sender()

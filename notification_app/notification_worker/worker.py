import argparse
import asyncio
import base64
import json
import os
from datetime import datetime
from typing import Any, Awaitable

import telegram
from aio_pika import ExchangeType, IncomingMessage, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from common.message import NotificationMessage

from notification_app.notification_worker.config import Config, read_config
from notification_app.repository import AsyncNotificationRepository
from notification_app.tg.constants import DEBUG_GROUP_CHAT_ID


class NotificationWorker:
    def __init__(self, repo: AsyncNotificationRepository, tg_token: str, mq_url: str):
        self.repo = repo
        self.bot = telegram.Bot(token=tg_token)
        self.mq_url = mq_url

    async def process_message(self, message: AbstractIncomingMessage):
        async with message.process():
            body = message.body.decode("utf-8")
            print(" [x] Received message")
            message_data = json.loads(body)
            notification_message = NotificationMessage(**message_data)
            org = await self.repo.get_organization_by_id(notification_message.org_id)
            student = await self.repo.get_user_account_by_id(notification_message.main_actor_id)
            text = (
                f"🏢 Organization: {org.org_name if org is not None else None}\n"
                f"🕒 Time: {notification_message.timestamp}\n"
                f"👤 Actor: {student.user_name if student is not None else None}\n"
                f"💬 Message: {notification_message.event_type}"
            )
            subs = await self.repo.get_subscriptions_by_student_id(
                org_id=org.id if org is not None else None,
                event_type=notification_message.event_type,
                student_id=notification_message.main_actor_id,
            )
            print(subs)
            image_binary = base64.b64decode(notification_message.image)
            # Handle image if provided

            if notification_message.image:
                await self.bot.send_photo(DEBUG_GROUP_CHAT_ID, photo=image_binary, caption=text)

                for sub in subs:
                    await self.bot.send_photo(sub.telegram_chat_id, photo=image_binary, caption=text)

            else:
                await self.bot.send_message(DEBUG_GROUP_CHAT_ID, text)

                for sub in subs:
                    await self.bot.send_message(sub.telegram_chat_id, text=text)

            await self.repo.create_event(
                org_id=notification_message.org_id,
                event_type=notification_message.event_type,
                timestamp=datetime.strptime(notification_message.timestamp, "%Y-%m-%d %H:%M:%S"),
                student_id=notification_message.main_actor_id,
            )
            print(" [x] Done")

    async def run(self):
        connection = await connect_robust(self.mq_url)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            # Declare the queue
            queue = await channel.declare_queue("notification", durable=True)

            print(" [*] Waiting for notifications. To exit press CTRL+C")
            # Consume messages
            await queue.consume(self.process_message)

            # Keep the event loop running
            await asyncio.Future()


def parse_args():
    parser = argparse.ArgumentParser(
        prog="notification worker",
        description="worker service for sending notifications",
    )
    parser.add_argument(
        "--config_path",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "config.yaml"),
        help="path to the configuration file",
    )
    return parser.parse_args()


async def worker():
    args = parse_args()
    config = read_config(args.config_path)
    repo = AsyncNotificationRepository(config.db)
    worker = NotificationWorker(repo, config.telegram_token, config.message_queue.get_amqp_url())

    await worker.run()


if __name__ == "__main__":
    asyncio.run(worker())

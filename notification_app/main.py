import argparse
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler

from notification_app.config import Config, read_config
from notification_app.repository import AsyncNotificationRepository
from notification_app.tg.add_subscription_conv import get_add_subscription_conv
from notification_app.tg.contact_support import get_contact_support_conv
from notification_app.tg.help_conv import help
from notification_app.tg.main_conv import get_main_conv, start_v2
from notification_app.tg.manage_subscription_conv import get_manage_subscription_conv

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main_telegram_bot(config: Config, repo: AsyncNotificationRepository) -> None:
    """Start the bot."""
    # Create the Application and pass it your token
    application = Application.builder().token(config.telegram_token).build()
    application.bot_data["repo"] = repo

    # help command handler
    application.add_handler(CommandHandler("help", help))
    # add subsription handler
    application.add_handler(get_add_subscription_conv(nested=False))
    # add manage subscription handler
    application.add_handler(get_manage_subscription_conv(nested=False))
    # add contact support handler
    application.add_handler(get_contact_support_conv(nested=False))
    # main dialog handler
    application.add_handler(CommandHandler("start", start_v2))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    parser = argparse.ArgumentParser(
        prog="telegram bot",
        description="telegram bot service for sending notifications",
    )
    parser.add_argument(
        "--config_path",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "config.yaml"),
        help="path to the configuration file",
    )
    args = parser.parse_args()

    config = read_config(args.config_path)
    repo = AsyncNotificationRepository(config.db)
    main_telegram_bot(config, repo)


if __name__ == "__main__":
    main()

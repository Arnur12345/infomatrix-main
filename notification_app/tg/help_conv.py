from telegram import Update
from telegram.ext import ContextTypes

from .constants import END


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /help is issued."""
    if update.callback_query:
        await update.callback_query.answer()
    text = """
<b>Commands overview</b>
The list of commands available are:
• /start - Start the bot conversation
• /help - List of commands available
• /manage - Manage your current subscriptions
• /subscribe - Subscribe to a new notification
• /contact_support - Get in touch with our support team
"""
    if update.message:
        await update.message.reply_html(text)

    return END

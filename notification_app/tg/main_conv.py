from common.models import EventType
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from notification_app.repository import AsyncNotificationRepository

from .add_subscription_conv import get_add_subscription_conv
from .constants import END, Constants, States
from .contact_support import get_contact_support_conv
from .exceptions import CallbackQueryNotSetError, MessageNotSetError, UserDataNotSetError
from .manage_subscription_conv import get_manage_subscription_conv
from .telegram_utils import build_menu


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    if update.message:
        await update.message.reply_text("Okay, bye.")

    return END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in end")

    await update.callback_query.answer()

    text = "See you around!"
    await update.callback_query.edit_message_text(text=text)

    return END


# TEMPORARY FIX
async def start_v2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user_name = update.effective_user.full_name if update.effective_user else "my friend"
    text = f"""
<b>Hello {user_name}! 👋</b>

I am your <i>Smart Kyoz assistant</i> 🤖

I'm here to help you with your notifications. Let's get started!

<b>What would you like to do?</b>
• Add your subscriptions 🔔 - /subscribe
• Manage your subscriptions 📬 - /manage
• Get help and support ❓ - /contact_support

Please use the commands above to navigate.
"""
    if update.message:
        await update.message.reply_html(text)

    return END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Send a message when the command /start is issued."""
    user_name = update.effective_user.full_name if update.effective_user else "my friend"
    print("in start")
    text = f"""
<b>Hello {user_name}! 👋</b>

I am your <i>Smart Kyoz assistant</i> 🤖

I'm here to help you with your notifications. Let's get started!

<b>What would you like to do?</b>
• Add your subscriptions 🔔
• Manage your subscriptions 📬
• Get help and support ❓

Please use the buttons below to navigate.
"""
    button_list = [
        InlineKeyboardButton("Add 🔔", callback_data=Constants.ADD_SUBSCRIPTION),
        InlineKeyboardButton("Manage 📬", callback_data=Constants.SHOWING_SUBSCRIPTIONS),
        InlineKeyboardButton("Get support ❓", callback_data=Constants.CONTACT_SUPPORT),
        InlineKeyboardButton("Done", callback_data=str(END)),
    ]
    menu = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    if update.message is not None:
        await update.message.reply_html(text, reply_markup=menu)
    elif update.callback_query is not None:
        await update.callback_query.edit_message_text(text, reply_markup=menu)

    return States.SELECTING_ACTION


def get_main_conv() -> ConversationHandler:
    entry_points = [
        CommandHandler("start", start),
    ]
    states = {
        States.SHOWING: [CallbackQueryHandler(start, pattern="^" + str(END) + "$")],
        States.SELECTING_ACTION: [
            get_add_subscription_conv(nested=True),
            get_manage_subscription_conv(nested=True),
            get_contact_support_conv(nested=True),
            CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
        ],
        States.STOPPING: [CommandHandler("start", start)],
    }

    fallbacks = [CommandHandler("stop", stop)]
    map_to_parent = None

    main_conv = ConversationHandler(
        entry_points=entry_points,  # type: ignore
        states=states,  # type: ignore
        fallbacks=fallbacks,  # type: ignore
        map_to_parent=map_to_parent,
    )

    return main_conv

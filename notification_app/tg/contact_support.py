import datetime

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .constants import DEBUG_GROUP_CHAT_ID, END, Constants, States
from .exceptions import CallbackQueryNotSetError, MessageNotSetError


async def contact_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if update.effective_chat is None:
        raise ValueError("Effective chat is None in contact_support")

    text = """
📢 **We value your feedback\\!**

Please share your feedback or describe any problem you encountered in as much detail as possible\\. 
Kindly keep it all in **ONE MESSAGE** to help us understand and assist you better\\. 📝

Thank you for helping us improve\\! 🙏
"""

    if update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, parse_mode="MarkdownV2")
    elif update.message is not None:
        await update.message.reply_text(text, parse_mode="MarkdownV2")

    return States.TYPING


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user feedback."""
    if update.message is None:
        raise MessageNotSetError("No message in handle_feedback")

    bot = update.get_bot()
    # send the message our debug group
    d = {
        "full_name": update.effective_user.full_name if update.effective_user is not None else None,
        "username": update.effective_user.username if update.effective_user is not None else None,
        "chat_id": update.effective_chat.id if update.effective_chat is not None else None,
    }
    feedback = (
        f"🕒 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"👤 User: {d['full_name']} {d['username']}\n"
        f"🆔 Chat ID: {d['chat_id']}\n"
        f"💬 Message: {update.message.text}"
    )
    await bot.send_message(chat_id=DEBUG_GROUP_CHAT_ID, text=feedback)

    await update.message.reply_text("Thank you for your feedback! We will get back to you soon.")

    return END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in end")
    await update.callback_query.answer()

    text = "See you around!"
    await update.callback_query.edit_message_text(text=text)

    return END


async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Completely end conversation from within nested conversation."""
    if update.message is None:
        raise MessageNotSetError("No message in stop_nested")
    await update.message.reply_text("Okay, bye.")

    return States.STOPPING


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    if update.message is None:
        raise MessageNotSetError("No message in stop")
    await update.message.reply_text("Okay, bye.")

    return END


def get_contact_support_conv(
    nested: bool = True,
) -> ConversationHandler:
    entry_points = [
        CallbackQueryHandler(contact_support, pattern="^" + Constants.CONTACT_SUPPORT + "$"),
        CommandHandler("contact_support", contact_support),
    ]

    states = {States.TYPING: [MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=handle_feedback)]}

    fallbacks = [
        CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
        CommandHandler("stop", stop_nested) if nested else CommandHandler("stop", stop),  # type: ignore
    ]
    map_to_parent = (
        {
            # Return to top level menu
            END: States.SHOWING,
            # End conversation altogether
            States.STOPPING: END,
        }
        if nested
        else None
    )

    add_subsription_conv = ConversationHandler(
        entry_points=entry_points,  # type: ignore
        states=states,  # type: ignore
        fallbacks=fallbacks,  # type: ignore
        map_to_parent=map_to_parent,
    )

    return add_subsription_conv

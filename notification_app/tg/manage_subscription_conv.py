from common.models import EventType
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from notification_app.repository import AsyncNotificationRepository

from .constants import END, Constants, States
from .exceptions import CallbackQueryNotSetError, MessageNotSetError, UserDataNotSetError
from .telegram_utils import build_menu


async def show_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    repo: AsyncNotificationRepository = context.bot_data["repo"]

    if update.effective_chat is None:
        raise ValueError("Effective chat is None in show_subscriptions")
    # Fetch organizations and subscriptions
    subs_and_orgs = await repo.get_subscriptions_and_orgs_by_tg_chat_id(update.effective_chat.id)
    button_list, button_texts = [], set()
    for sub, org in subs_and_orgs:
        button_text = ""
        if sub.student_id is not None:
            student = await repo.get_user_account_by_id(sub.student_id)
            if student is None:
                raise ValueError("Student is None in show_subscriptions")
            button_text = f"{org.org_name} - entrance/exit - {student.user_name}"
        else:
            button_text = f"{org.org_name} - {sub.event_type.value}"

        if button_text not in button_texts:
            button_texts.add(button_text)
            button_list.append(
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"{Constants.DELETE_SUBSCRIPTIONS}_{sub.id}",
                )
            )

    text = "Choose a subscription to delete"
    subscription_selection = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=1, footer_buttons=InlineKeyboardButton("Done", callback_data=str(END)))
    )
    if update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=subscription_selection)
    elif update.message is not None:
        await update.message.reply_text(text, reply_markup=subscription_selection)

    return States.DELETING_SUBSCRIPTION


async def delete_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in delete_subscriptions")
    if update.effective_chat is None:
        raise ValueError("Effective chat is None in delete_subscriptions")
    if update.callback_query.data is None:
        raise UserDataNotSetError("No data in delete_subscriptions")

    repo: AsyncNotificationRepository = context.bot_data["repo"]
    [_, sub_id] = update.callback_query.data.split("_", 1)
    print(sub_id, _)

    subscription = await repo.get_subscription_by_id(sub_id)
    print(subscription)
    if subscription is None:
        raise ValueError("Subscription is None in delete_subscriptions")

    if subscription.event_type in (EventType.STUDENT_ENTRANCE, EventType.STUDENT_EXIT):
        subs1 = await repo.get_subscriptions_by_filters(
            org_id=None,
            student_id=subscription.student_id,
            tg_chat_id=update.effective_chat.id,
            event_type=EventType.STUDENT_ENTRANCE,
        )
        subs2 = await repo.get_subscriptions_by_filters(
            org_id=None,
            student_id=subscription.student_id,
            tg_chat_id=update.effective_chat.id,
            event_type=EventType.STUDENT_EXIT,
        )
        subs = subs1 + subs2
        # delete subscriptions
        for sub in subs:
            await repo.delete_subscription_by_id(sub.id)
            print(f"deleting subscription {sub.id}, {sub.event_type}")
    else:
        await repo.delete_subscription_by_id(sub_id)
        print(f"deleting subscription {subscription.id}, {subscription.event_type}")

    await update.callback_query.answer("Chosen subscription deleted")
    menu = build_menu(
        [],
        n_cols=1,
        footer_buttons=InlineKeyboardButton(
            "<< Back to your subscriptions", callback_data=Constants.SHOWING_SUBSCRIPTIONS
        ),
    )
    await update.callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(menu))

    return States.MANAGING_SUBSCRIPTION


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


def get_manage_subscription_conv(
    nested: bool = True,
) -> ConversationHandler:
    entry_points = [
        CallbackQueryHandler(show_subscriptions, pattern="^" + Constants.SHOWING_SUBSCRIPTIONS + "$"),
        CommandHandler("manage", show_subscriptions),
    ]

    states = {
        States.MANAGING_SUBSCRIPTION: [
            CallbackQueryHandler(show_subscriptions, pattern="^" + Constants.SHOWING_SUBSCRIPTIONS + "$"),
        ],
        States.DELETING_SUBSCRIPTION: [
            CallbackQueryHandler(
                delete_subscriptions, pattern="^" + f"{Constants.DELETE_SUBSCRIPTIONS}_[a-zA-Z0-9-]+" + "$"
            ),
        ],
    }

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

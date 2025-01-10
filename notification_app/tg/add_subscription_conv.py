import logging

from common.models import EventType
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from notification_app.repository import AsyncNotificationRepository

from .constants import DEFAULT_SUBSCRIPTIONS_DICT, END, Constants, States
from .exceptions import CallbackQueryNotSetError, MessageNotSetError, UserDataNotSetError
from .telegram_utils import build_menu


async def select_organization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action: Adding parent/child or show data."""

    repo: AsyncNotificationRepository = context.bot_data["repo"]
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in select_organization")
    context.user_data.clear()
    context.user_data[Constants.START_OVER] = True

    # Fetch the organizations from the repository without manually managing the session
    organizations = await repo.get_organizations()

    # Extract organization names and ids
    button_list = [InlineKeyboardButton(org.org_name, callback_data=str(org.id)) for org in organizations]

    text = "Choose your organization"
    company_selection = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, footer_buttons=InlineKeyboardButton("Done", callback_data=str(END)))
    )
    if update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=company_selection)
    elif update.message is not None:
        await update.message.reply_text(text, reply_markup=company_selection)

    return States.SELECTING_FEATURES


async def select_features(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in select_features")
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in select_features")
    if update.callback_query.data is None:
        raise CallbackQueryNotSetError("No data in callback query in select_features")

    if context.user_data.get(Constants.START_OVER) is True:
        context.user_data.clear()
        context.user_data[Constants.START_OVER] = False
        context.user_data[Constants.SUBSCRIPTIONS] = DEFAULT_SUBSCRIPTIONS_DICT
        context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION] = update.callback_query.data

    # handle cancel buttons
    if update.callback_query.data.startswith("!"):
        feature, *args = update.callback_query.data[1:].split("_")

        if feature == Constants.SMOKING:
            context.user_data[Constants.SUBSCRIPTIONS][Constants.SMOKING] = False
        elif feature == Constants.FIGHTING:
            context.user_data[Constants.SUBSCRIPTIONS][Constants.FIGHTING] = False
        elif feature == Constants.WEAPON:
            context.user_data[Constants.SUBSCRIPTIONS][Constants.WEAPON] = False
        elif feature == Constants.LYING_MAN:
            context.user_data[Constants.SUBSCRIPTIONS][Constants.LYING_MAN] = False
        elif feature == Constants.STUDENT_ENTRANCE_EXIT:
            assert len(args) == 2
            stud_id, _ = args
            if stud_id == "":
                context.user_data[Constants.SUBSCRIPTIONS][Constants.STUDENT_ENTRANCE_EXIT].clear()
            else:
                context.user_data[Constants.SUBSCRIPTIONS][Constants.STUDENT_ENTRANCE_EXIT].remove(stud_id)

    text = "Add your subscriptions"
    button_list = [
        InlineKeyboardButton("Smoking Detection", callback_data=Constants.SMOKING),
        InlineKeyboardButton("Fighting Detecttion", callback_data=Constants.FIGHTING),
        InlineKeyboardButton("Weapon Detection", callback_data=Constants.WEAPON),
        InlineKeyboardButton("Lying Man Detection", callback_data=Constants.LYING_MAN),
        InlineKeyboardButton("Student Entrance/Exit", callback_data=Constants.STUDENT_ENTRANCE_EXIT),
    ]
    menu = InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=2,
            footer_buttons=InlineKeyboardButton(">> Save selection and back to organizations", callback_data=str(END)),
        )
    )
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text, reply_markup=menu)

    return States.FEATURE_HANDLING


async def smoking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in smoking")
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in smoking")
    context.user_data[Constants.SUBSCRIPTIONS][Constants.SMOKING] = True

    text = "You have selected Smoking"
    await update.callback_query.answer(text)

    button_list = [InlineKeyboardButton("Unselect Smoking Detection", callback_data=f"!{Constants.SMOKING}")]
    menu = InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=2,
            footer_buttons=InlineKeyboardButton("<< Back to features", callback_data=Constants.SMOKING),
        )
    )
    await update.callback_query.edit_message_text(text, reply_markup=menu)

    return States.SELECTING_FEATURES


async def fighting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in fighting")
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in fighting")

    context.user_data[Constants.SUBSCRIPTIONS][Constants.FIGHTING] = True
    text = "You have selected Fighting"

    button_list = [InlineKeyboardButton("Unselect Fighting Detection", callback_data=f"!{Constants.FIGHTING}")]
    menu = InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=2,
            footer_buttons=InlineKeyboardButton("<< Back to features", callback_data=Constants.FIGHTING),
        )
    )
    await update.callback_query.answer(text)
    await update.callback_query.edit_message_text(text, reply_markup=menu)

    return States.SELECTING_FEATURES


async def weapon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in weapon")
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in weapon")

    context.user_data[Constants.SUBSCRIPTIONS][Constants.WEAPON] = True
    text = "You have selected Weapon Detection"

    button_list = [InlineKeyboardButton("Unselect Weapon Detection", callback_data=f"!{Constants.WEAPON}")]
    menu = InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=2,
            footer_buttons=InlineKeyboardButton("<< Back to features", callback_data=Constants.WEAPON),
        )
    )
    await update.callback_query.answer(text)
    await update.callback_query.edit_message_text(text, reply_markup=menu)

    return States.SELECTING_FEATURES


async def lying_man(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in weapon")
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in weapon")

    context.user_data[Constants.SUBSCRIPTIONS][Constants.LYING_MAN] = True
    text = "You have selected Lying Man"

    button_list = [InlineKeyboardButton("Unselect Lying Man Detection", callback_data=f"!{Constants.LYING_MAN}")]
    menu = InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=2,
            footer_buttons=InlineKeyboardButton("<< Back to features", callback_data=Constants.LYING_MAN),
        )
    )
    await update.callback_query.answer(text)
    await update.callback_query.edit_message_text(text, reply_markup=menu)

    return States.SELECTING_FEATURES


async def showing_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Display a list of students to subscribe to their entrance/exit events."""
    repo: AsyncNotificationRepository = context.bot_data["repo"]
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in showing_students")
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in showing_students")
    if update.callback_query.data is None:
        raise CallbackQueryNotSetError("No data in callback query in showing_students")

    # handle cancel buttons
    if update.callback_query.data.startswith("!"):
        feature, *args = update.callback_query.data[1:].split("_")
        assert feature == Constants.STUDENT_ENTRANCE_EXIT
        assert len(args) == 2
        stud_id, _ = args
        if stud_id == "":
            context.user_data[Constants.SUBSCRIPTIONS][Constants.STUDENT_ENTRANCE_EXIT].clear()
        else:
            context.user_data[Constants.SUBSCRIPTIONS][Constants.STUDENT_ENTRANCE_EXIT].remove(stud_id)

    org_id = context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION]

    # getting list of students from database
    students = await repo.get_user_accounts_by_org(org_id)

    # creating buttons from student list
    button_list = [
        InlineKeyboardButton(
            stud.user_name,
            callback_data=f"{Constants.STUDENT_ENTRANCE_EXIT}_{stud.id}",
        )
        for stud in students
    ]

    # creating interface for choosing student
    text = "Choose your student"
    student_selection = InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=2,
            header_buttons=[
                InlineKeyboardButton("<< Back to features", callback_data=Constants.FEATURES),
                InlineKeyboardButton(">> All students", callback_data=f"{Constants.STUDENT_ENTRANCE_EXIT}_"),
            ],
        )
    )

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text, reply_markup=student_selection)

    return States.SELECTING_STUDENT


async def select_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    repo: AsyncNotificationRepository = context.bot_data["repo"]
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in select_student")
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in select_student")
    if update.callback_query.data is None:
        raise CallbackQueryNotSetError("No data in callback query in select_student")

    _, stud_id = update.callback_query.data.split("_", 1)
    student = await repo.get_user_account_by_id(stud_id)
    if stud_id == "":
        org_id = context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION]
        students = await repo.get_user_accounts_by_org(org_id)
        text = f"You have selected all students in organization."

        for student in students:
            context.user_data[Constants.SUBSCRIPTIONS][Constants.STUDENT_ENTRANCE_EXIT].add(student.id)
    else:
        if student is None:
            raise ValueError(f"Student with id {stud_id} not found")
        context.user_data[Constants.SUBSCRIPTIONS][Constants.STUDENT_ENTRANCE_EXIT].add(stud_id)
        text = f"You have selected the student {student.user_name}."

    await update.callback_query.answer(text)

    button_list = [
        InlineKeyboardButton(
            f"Unselect Student {student.user_name}" if stud_id != "" else "Unselect all students",
            callback_data=f"!{Constants.STUDENT_ENTRANCE_EXIT}_{stud_id}",
        )
    ]
    menu = InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=2,
            footer_buttons=InlineKeyboardButton(
                "<< Back to students", callback_data=f"{Constants.STUDENT_ENTRANCE_EXIT}"
            ),
        )
    )
    await update.callback_query.edit_message_text(text, reply_markup=menu)

    return States.FEATURE_HANDLING


async def go_back_to_select_features(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    return await select_features(update, context)


async def save_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    repo: AsyncNotificationRepository = context.bot_data["repo"]
    if context.user_data is None:
        raise UserDataNotSetError("User data not set in context in save_subscription")
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in save_subscription")
    if context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION] == "":
        raise ValueError("Organization not set in save subscription")

    if update.effective_user is not None:
        async with repo.session() as session:
            if context.user_data[Constants.SUBSCRIPTIONS][Constants.SMOKING] is True:
                logging.info(f"Creating subscription for smoking for user {update.effective_user.id}")
                result = await repo.get_subscriptions_by_filters(
                    org_id=context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                    student_id=None,
                    tg_chat_id=update.effective_user.id,
                    event_type=EventType.SMOKING,
                    session=session,
                )
                if len(result) == 0:
                    await repo.create_subscription(
                        context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                        tg_chat_id=update.effective_user.id,
                        event_type=EventType.SMOKING,
                        session=session,
                        commit=False,
                    )
            if context.user_data[Constants.SUBSCRIPTIONS][Constants.FIGHTING] is True:
                logging.info(f"Creating subscription for fighting for user {update.effective_user.id}")
                result = await repo.get_subscriptions_by_filters(
                    org_id=context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                    student_id=None,
                    tg_chat_id=update.effective_user.id,
                    event_type=EventType.FIGHTING,
                    session=session,
                )
                if len(result) == 0:
                    await repo.create_subscription(
                        context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                        tg_chat_id=update.effective_user.id,
                        event_type=EventType.FIGHTING,
                        session=session,
                        commit=False,
                    )
            if context.user_data[Constants.SUBSCRIPTIONS][Constants.WEAPON] is True:
                logging.info(f"Creating subscription for weapon for user {update.effective_user.id}")
                result = await repo.get_subscriptions_by_filters(
                    org_id=context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                    student_id=None,
                    tg_chat_id=update.effective_user.id,
                    event_type=EventType.WEAPON,
                    session=session,
                )
                if len(result) == 0:
                    await repo.create_subscription(
                        context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                        tg_chat_id=update.effective_user.id,
                        event_type=EventType.WEAPON,
                        session=session,
                        commit=False,
                    )
            if context.user_data[Constants.SUBSCRIPTIONS][Constants.LYING_MAN] is True:
                logging.info(f"Creating subscription for lying man for user {update.effective_user.id}")
                result = await repo.get_subscriptions_by_filters(
                    org_id=context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                    student_id=None,
                    tg_chat_id=update.effective_user.id,
                    event_type=EventType.LYING_MAN,
                    session=session,
                )
                if len(result) == 0:
                    await repo.create_subscription(
                        context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                        tg_chat_id=update.effective_user.id,
                        event_type=EventType.LYING_MAN,
                        session=session,
                        commit=False,
                    )

            for student_id in context.user_data[Constants.SUBSCRIPTIONS][Constants.STUDENT_ENTRANCE_EXIT]:
                logging.info(
                    f"Creating subscription for student entrance/exit for user {update.effective_user.id} for {student_id}"
                )
                result = await repo.get_subscriptions_by_filters(
                    org_id=context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                    student_id=student_id,
                    tg_chat_id=update.effective_user.id,
                    event_type=EventType.STUDENT_ENTRANCE,
                    session=session,
                )
                if len(result) == 0:
                    await repo.create_subscription(
                        context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                        tg_chat_id=update.effective_user.id,
                        event_type=EventType.STUDENT_ENTRANCE,
                        student_id=student_id,
                        session=session,
                        commit=False,
                    )
                    await repo.create_subscription(
                        context.user_data[Constants.SUBSCRIPTIONS][Constants.ORGANIZATION],
                        tg_chat_id=update.effective_user.id,
                        event_type=EventType.STUDENT_EXIT,
                        student_id=student_id,
                        session=session,
                        commit=False,
                    )

            await session.commit()

    await update.callback_query.answer("Saved your subscriptions")

    return await select_organization(update, context)


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    if update.callback_query is None:
        raise CallbackQueryNotSetError("No callback query in save_subscription")
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


def get_add_subscription_conv(
    nested: bool = True,
) -> ConversationHandler:
    entry_points = [
        CallbackQueryHandler(select_organization, pattern="^" + Constants.ADD_SUBSCRIPTION + "$"),
        CommandHandler("subscribe", select_organization),
    ]

    states = {
        States.SELECTING_ORGANIZATION: [
            CallbackQueryHandler(select_organization),
        ],
        States.SELECTING_FEATURES: [
            CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
            CallbackQueryHandler(select_features),
        ],
        States.FEATURE_HANDLING: [
            CallbackQueryHandler(smoking, pattern="^" + Constants.SMOKING + "$"),
            CallbackQueryHandler(fighting, pattern="^" + Constants.FIGHTING + "$"),
            CallbackQueryHandler(weapon, pattern="^" + Constants.WEAPON + "$"),
            CallbackQueryHandler(lying_man, pattern="^" + Constants.LYING_MAN + "$"),
            CallbackQueryHandler(
                showing_students,
                pattern="^" + f"{Constants.STUDENT_ENTRANCE_EXIT}" + "|"
                f"!{Constants.STUDENT_ENTRANCE_EXIT}_(?:[a-zA-Z0-9-]+)?"
                "$",
            ),
            CallbackQueryHandler(save_subscription, pattern="^" + str(END) + "$"),
        ],
        States.SELECTING_STUDENT: [
            CallbackQueryHandler(go_back_to_select_features, pattern="^" + Constants.FEATURES + "$"),
            CallbackQueryHandler(select_student),
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

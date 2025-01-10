from enum import Enum

from telegram.ext import ConversationHandler


class States(str, Enum):
    # add subscription
    ADDING_SUBSCRIPTION = "a-s"
    SELECTING_ORGANIZATION = "s-o"
    SELECTING_FEATURES = "s-f"
    SELECTING_STUDENT = "s-s"
    FEATURE_HANDLING = "f-h"
    REMOVING_SUBSCRIPTION = "r-s"
    STOPPING = "st"
    # manage subscription
    MANAGING_SUBSCRIPTION = "m-s"
    DELETING_SUBSCRIPTION = "d-s"
    # get support
    GETTING_SUPPORT = "g-s"
    TYPING = "ty"
    # main conversation
    SHOWING = "sh"
    SELECTING_ACTION = "s-a"


# Shortcut for ConversationHandler.END
END = ConversationHandler.END


class Constants(str, Enum):
    # adding subs
    ADD_SUBSCRIPTION = "a-s"
    SMOKING = "s"
    FIGHTING = "f"
    STUDENT_ENTRANCE_EXIT = "s-e-e"
    ORGANIZATION = "o"
    START_OVER = "s-o"
    FEATURES = "fea"
    SUBSCRIPTIONS = "su"
    WEAPON = "w"
    LYING_MAN = "l-m"
    # managing subs
    SHOWING_SUBSCRIPTIONS = "sh-s"
    DELETE_SUBSCRIPTIONS = "d-s"
    # contact support
    CONTACT_SUPPORT = "c-s"


DEFAULT_SUBSCRIPTIONS_DICT = {
    Constants.ORGANIZATION: "",
    Constants.SMOKING: False,
    Constants.WEAPON: False,
    Constants.FIGHTING: False,
    Constants.LYING_MAN: False,
    Constants.STUDENT_ENTRANCE_EXIT: set(),
}

DEBUG_GROUP_CHAT_ID = -1002445876781

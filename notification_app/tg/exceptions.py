class UserDataNotSetError(Exception):
    def __init__(self, message):
        super().__init__(message)  # Call the base class constructor

    def __str__(self):
        return f"{self.args[0]}"


class CallbackQueryNotSetError(Exception):
    def __init__(self, message):
        super().__init__(message)  # Call the base class constructor

    def __str__(self):
        return f"{self.args[0]}"


class MessageNotSetError(Exception):
    def __init__(self, message):
        super().__init__(message)  # Call the base class constructor

    def __str__(self):
        return f"{self.args[0]}"

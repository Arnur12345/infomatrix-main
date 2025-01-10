from typing import Protocol


class BaseNotificationProvider(Protocol):
    def send_notification(self, recipient, message, **kwargs) -> None: ...

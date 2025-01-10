from dataclasses import dataclass

from .models import EventType


@dataclass
class NotificationMessage:
    event_type: EventType = EventType.FIGHTING
    org_id: str | None = None
    main_actor_id: str | None = None
    actor_ids: list[str] | None = None
    image: str | None = None
    timestamp: str | None = None

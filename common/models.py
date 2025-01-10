from datetime import datetime
from enum import Enum

import numpy as np
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import ARRAY, INTEGER

from kit.utils import string_uuid


class EventType(str, Enum):
    FIGHTING = "fighting"
    STUDENT_ENTRANCE = "entrance"
    STUDENT_EXIT = "exit"
    SMOKING = "smoking"
    WEAPON = "weapon"
    LYING_MAN = "lying_man"


class UserRole(str, Enum):
    STUDENT = "student"
    PARENT = "parent"
    STAFF = "staff"
    ADMIN = "admin"


class Base(MappedAsDataclass, DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        init=False,
    )


class Organization(Base):
    __tablename__ = "organization"

    org_name: Mapped[str] = mapped_column(unique=True)
    id: Mapped[str] = mapped_column(default_factory=string_uuid, primary_key=True)


class UserAccount(Base):
    __tablename__ = "account"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organization.id"))
    user_name: Mapped[str] = mapped_column()
    user_role: Mapped[UserRole] = mapped_column()
    user_login: Mapped[str] = mapped_column()
    password_hash: Mapped[str] = mapped_column()
    id: Mapped[str] = mapped_column(default_factory=string_uuid, primary_key=True)


class FaceEncoding(Base):
    __tablename__ = "face_encoding"

    face_encoding: Mapped[bytes] = mapped_column()
    user_id: Mapped[str] = mapped_column(ForeignKey("account.id"))
    id: Mapped[str] = mapped_column(default_factory=string_uuid, primary_key=True)

    @property
    def embedding(self) -> np.ndarray:
        return np.frombuffer(self.face_encoding, dtype=np.float64)


class Subscription(Base):
    __tablename__ = "subscription"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organization.id"))
    telegram_chat_id: Mapped[int] = mapped_column()
    event_type: Mapped[EventType] = mapped_column()
    student_id: Mapped[str | None] = mapped_column(ForeignKey("account.id"), nullable=True, default=None)

    id: Mapped[str] = mapped_column(default_factory=string_uuid, primary_key=True)


class Event(Base):
    __tablename__ = "event"

    event_type: Mapped[EventType] = mapped_column()
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organization.id"), nullable=True, default=None)
    timestamp: Mapped[datetime | None] = mapped_column(nullable=True, default=None)
    student_id: Mapped[str | None] = mapped_column(ForeignKey("account.id"), nullable=True, default=None)
    id: Mapped[str] = mapped_column(default_factory=string_uuid, primary_key=True)
    camera_id: Mapped[str | None] = mapped_column(nullable=True, default=None)


class Schedule(Base):
    __tablename__ = "schedule"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organization.id"))
    start_time: Mapped[datetime | None] = mapped_column(nullable=True, default=None)
    end_time: Mapped[datetime | None] = mapped_column(nullable=True, default=None)
    id: Mapped[str] = mapped_column(default_factory=string_uuid, primary_key=True)

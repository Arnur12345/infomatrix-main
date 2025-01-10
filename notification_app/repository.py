import logging
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import TYPE_CHECKING, AsyncContextManager, AsyncGenerator, ContextManager, Coroutine, Protocol

from common.models import Base, Event, EventType, FaceEncoding, Organization, Subscription, UserAccount, UserRole
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from kit.dbx import DBConfig

logger = logging.getLogger()


class INotificationRepository(Protocol):
    def get_engine(self) -> AsyncEngine:
        """Returns the async engine used for database operations."""
        ...

    def get_sessionmaker(self) -> async_sessionmaker:
        """Returns the async sessionmaker bound to the async engine."""
        ...

    async def migrate_tables(self) -> None:
        """Runs the migration to create all necessary database tables."""
        ...

    # async def connect(self) -> Coroutine[Any, Any, AsyncContextManager[AsyncConnection]]:
    #     """Provides an async context-managed connection."""
    #     ...

    # async def session(self) -> Coroutine[Any, Any, AsyncContextManager[AsyncConnection]]:
    #     """Provides an async context-managed session."""
    #     ...

    async def create_organization(
        self, org_name: str, commit: bool = True, session: AsyncSession | None = None
    ) -> Organization:
        """Creates a new organization and returns it."""
        ...

    async def get_organization_by_id(self, org_id: str, session: AsyncSession | None = None) -> Organization | None:
        """Fetches an organization by its ID."""
        ...

    async def get_organization_by_name(self, org_name: str, session: AsyncSession | None = None) -> Organization | None:
        """Fetches an organization by its name."""
        ...

    async def get_organizations(self, session: AsyncSession | None = None) -> list[Organization]:
        """Retrieves all organizations."""
        ...

    async def delete_organization_by_id(
        self, org_id: str, commit: bool = True, session: AsyncSession | None = None
    ) -> None:
        """Deletes an organization by its ID."""
        ...

    async def create_user_account(
        self, org_id: str, user_name: str, user_role: str, commit: bool = True, session: AsyncSession | None = None
    ) -> UserAccount:
        """Creates a new user account and returns it."""
        ...

    async def get_user_account_by_id(self, user_id: str, session: AsyncSession | None = None) -> UserAccount | None:
        """Fetches a user account by its ID."""
        ...

    async def get_user_accounts_by_org(self, org_id: str, session: AsyncSession | None = None) -> list[UserAccount]:
        """Fetches all user accounts associated with a specific organization."""
        ...

    async def delete_user_account_by_id(
        self, user_id: str, commit: bool = True, session: AsyncSession | None = None
    ) -> None:
        """Deletes a user account by its ID."""
        ...

    async def create_face_encoding(
        self, user_id: str, face_encoding: bytes, commit: bool = True, session: AsyncSession | None = None
    ) -> FaceEncoding:
        """Creates and stores a face encoding for a specific user."""
        ...

    async def get_face_encodings_by_user_id(
        self, user_id: str, session: AsyncSession | None = None
    ) -> list[FaceEncoding]:
        """Fetches face encodings associated with a specific user."""
        ...

    async def get_face_encodings_by_org(self, org_id: str, session: AsyncSession | None = None) -> list[FaceEncoding]:
        """Fetches face encodings associated with all users in a specific organization."""
        ...

    async def delete_face_encoding_by_id(
        self, face_enc_id: str, commit: bool = True, session: AsyncSession | None = None
    ) -> None:
        """Deletes a face encoding by its ID."""
        ...


class AsyncNotificationRepository:
    def __init__(self, config_db: DBConfig) -> None:
        self._engine = create_async_engine(config_db.async_connection_string())
        self._sessionmaker = async_sessionmaker(bind=self._engine)

    def get_engine(self) -> AsyncEngine:
        return self._engine

    def get_sessionmaker(self) -> async_sessionmaker:
        return self._sessionmaker

    async def migrate_tables(self):
        logger.info("Start migrating")

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Done migrating")

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("AsyncNotificationRepository is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_organization(
        self,
        org_name: str,
        commit: bool = True,
        session: AsyncSession | None = None,
    ) -> Organization:
        if session is not None:
            org = Organization(org_name=org_name)
            session.add(org)
            if commit:
                await session.commit()
                await session.refresh(org)
            return org

        # if no session is provided, create a new one
        async with self._sessionmaker() as session:
            org = Organization(org_name=org_name)
            session.add(org)
            await session.commit()
            await session.refresh(org)
            return org

    async def get_organization_by_id(self, org_id: str, session: AsyncSession | None = None) -> Organization | None:
        if session is not None:
            stmt = select(Organization).filter(Organization.id == org_id)
            result = await session.execute(stmt)
            return result.scalars().first()

        async with self._sessionmaker() as session:
            stmt = select(Organization).filter(Organization.id == org_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_organization_by_ids(
        self, org_ids: list[str], session: AsyncSession | None = None
    ) -> list[Organization]:
        stmt = select(Organization).where(Organization.id.in_(org_ids))

        # Use the provided session or create a new one
        if session is not None:
            result = await session.execute(stmt)
        else:
            async with self._sessionmaker() as session:
                result = await session.execute(stmt)

        return list(result.scalars().all())

    async def get_organization_by_name(self, org_name: str, session: AsyncSession | None = None) -> Organization | None:
        if session is not None:
            stmt = select(Organization).filter(Organization.org_name == org_name)
            result = await session.execute(stmt)
            return result.scalars().first()

        async with self._sessionmaker() as session:
            stmt = select(Organization).filter(Organization.org_name == org_name)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_organizations(self, session: AsyncSession | None = None) -> list[Organization]:
        if session is not None:
            stmt = select(Organization)
            result = await session.execute(stmt)
            return list(result.scalars().all())

        async with self._sessionmaker() as session:
            stmt = select(Organization)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def delete_organization_by_id(
        self,
        org_id: str,
        commit: bool = True,
        session: AsyncSession | None = None,
    ) -> None:
        if session is not None:
            stmt = delete(Organization).filter(Organization.id == org_id)
            await session.execute(stmt)
            if commit:
                await session.commit()
            return

        async with self._sessionmaker() as session:
            stmt = delete(Organization).filter(Organization.id == org_id)
            await session.execute(stmt)
            if commit:
                await session.commit()
            return

    # TODO: fix this
    async def create_user_account(
        self,
        org_id: str,
        user_name: str,
        user_role: UserRole,
        password_hash: str,
        user_login: str,
        commit: bool = True,
        session: AsyncSession | None = None,
    ) -> UserAccount:
        if session is not None:
            user = UserAccount(
                organization_id=org_id, user_name=user_name, user_role=user_role, password_hash="", user_login=""
            )
            session.add(user)
            if commit:
                await session.commit()
                await session.refresh(user)
            return user

        async with self._sessionmaker() as session:
            user = UserAccount(
                organization_id=org_id, user_name=user_name, user_role=user_role, password_hash="", user_login=""
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_user_account_by_id(self, user_id: str, session: AsyncSession | None = None) -> UserAccount | None:
        if session is not None:
            stmt = select(UserAccount).filter(UserAccount.id == user_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        async with self._sessionmaker() as session:
            stmt = select(UserAccount).filter(UserAccount.id == user_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_user_accounts_by_org(
        self,
        org_id: str,
        session: AsyncSession | None = None,
    ) -> list[UserAccount]:
        if session is not None:
            stmt = select(UserAccount).filter(UserAccount.organization_id == org_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        async with self._sessionmaker() as session:
            stmt = select(UserAccount).filter(UserAccount.organization_id == org_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def delete_user_account_by_id(
        self, user_id: str, commit: bool = True, session: AsyncSession | None = None
    ) -> None:
        if session is not None:
            stmt = delete(UserAccount).filter(UserAccount.id == user_id)
            await session.execute(stmt)
            if commit:
                await session.commit()
            return
        async with self._sessionmaker() as session:
            stmt = delete(UserAccount).filter(UserAccount.id == user_id)
            await session.execute(stmt)
            await session.commit()
            return

    async def create_face_encoding(
        self,
        user_id: str,
        face_encoding: bytes,
        commit: bool = True,
        session: AsyncSession | None = None,
    ) -> FaceEncoding:
        if session is not None:
            face = FaceEncoding(user_id=user_id, face_encoding=face_encoding)
            session.add(face)
            if commit:
                await session.commit()
                await session.refresh(face)
            return face
        async with self._sessionmaker() as session:
            face = FaceEncoding(user_id=user_id, face_encoding=face_encoding)
            session.add(face)
            await session.commit()
            await session.refresh(face)
            return face

    async def get_face_encodings_by_user_id(
        self,
        user_id: str,
        session: AsyncSession | None = None,
    ) -> list[FaceEncoding]:
        if session is not None:
            stmt = select(FaceEncoding).filter(FaceEncoding.user_id == user_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        async with self._sessionmaker() as session:
            stmt = select(FaceEncoding).filter(FaceEncoding.user_id == user_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_face_encodings_by_org(self, org_id: str, session: AsyncSession | None = None) -> list[FaceEncoding]:
        if session is not None:
            stmt = (
                select(FaceEncoding)
                .join(UserAccount, UserAccount.id == FaceEncoding.user_id)
                .filter(UserAccount.organization_id == org_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

        async with self._sessionmaker() as session:
            stmt = (
                select(FaceEncoding)
                .join(UserAccount, UserAccount.id == FaceEncoding.user_id)
                .filter(UserAccount.organization_id == org_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def delete_face_encoding_by_id(
        self,
        face_enc_id: str,
        commit: bool = True,
        session: AsyncSession | None = None,
    ) -> None:
        if session is not None:
            stmt = delete(FaceEncoding).filter(FaceEncoding.id == face_enc_id)
            await session.execute(stmt)
            if commit:
                await session.commit()
            return
        async with self._sessionmaker() as session:
            stmt = delete(FaceEncoding).filter(FaceEncoding.id == face_enc_id)
            await session.execute(stmt)
            await session.commit()
            return

    async def get_subscriptions_by_tg_chat_id(
        self, tg_chat_id: int, session: AsyncSession | None = None
    ) -> list[Subscription]:
        if session is not None:
            stmt = select(Subscription).filter(Subscription.telegram_chat_id == tg_chat_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        async with self._sessionmaker() as session:
            stmt = select(Subscription).filter(Subscription.telegram_chat_id == tg_chat_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_subscription_by_id(self, sub_id: str, session: AsyncSession | None = None) -> Subscription | None:
        stmt = select(Subscription).filter(Subscription.id == sub_id)
        if session is not None:
            result = await session.execute(stmt)
            return result.scalars().first()
        async with self._sessionmaker() as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_subscriptions_and_orgs_by_tg_chat_id(
        self, tg_chat_id: int, session: AsyncSession | None = None
    ) -> list[tuple[Subscription, Organization]]:
        stmt = (
            select(Subscription, Organization)
            .join(Organization, Subscription.organization_id == Organization.id)
            .filter(Subscription.telegram_chat_id == tg_chat_id)
        )

        # Use the provided session or create a new one
        if session is not None:
            result = await session.execute(stmt)
        else:
            async with self._sessionmaker() as session:
                result = await session.execute(stmt)

        # Use result.all() to retrieve tuples (Subscription, Organization)
        return [(row[0], row[1]) for row in result.all()]

    async def get_subscription_by_org_id(
        self,
        org_id: str,
        tg_chat_id: int | None = None,
        session: AsyncSession | None = None,
    ) -> list[Subscription]:
        if session is not None:
            stmt = select(Subscription).filter(Subscription.organization_id == org_id)
            if tg_chat_id:
                stmt = stmt.filter(Subscription.telegram_chat_id == tg_chat_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        async with self._sessionmaker() as session:
            stmt = select(Subscription).filter(Subscription.organization_id == org_id)
            if tg_chat_id:
                stmt = stmt.filter(Subscription.telegram_chat_id == tg_chat_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_subscriptions_by_student_id(
        self, org_id: str, student_id: str, event_type: EventType, session: AsyncSession | None = None
    ) -> list[Subscription]:
        stmt = select(Subscription).filter(
            Subscription.organization_id == org_id,
            Subscription.student_id == student_id,
            Subscription.event_type == event_type,
        )

        if session is not None:
            result = await session.execute(stmt)
            return list(result.scalars().all())
        async with self._sessionmaker() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_subscriptions_by_filters(
        self,
        org_id: str | None,
        student_id: str | None,
        tg_chat_id: int,
        event_type: EventType,
        session: AsyncSession | None = None,
    ) -> list[Subscription]:
        """Fetch subscriptions based on student_id and event type."""
        if org_id is not None:
            stmt = select(Subscription).filter(
                Subscription.organization_id == org_id,
                Subscription.student_id == student_id,
                Subscription.event_type == event_type,
                Subscription.telegram_chat_id == tg_chat_id,
            )
        else:
            stmt = select(Subscription).filter(
                Subscription.student_id == student_id,
                Subscription.event_type == event_type,
                Subscription.telegram_chat_id == tg_chat_id,
            )

        if session is not None:
            result = await session.execute(stmt)
            return list(result.scalars().all())

        async with self._sessionmaker() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def create_subscription(
        self,
        org_id: str,
        tg_chat_id: int,
        event_type: EventType,
        student_id: str | None = None,
        commit: bool = True,
        session: AsyncSession | None = None,
    ) -> Subscription:
        if session is not None:
            sub = Subscription(
                organization_id=org_id,
                telegram_chat_id=tg_chat_id,
                event_type=event_type,
                student_id=student_id,
            )
            session.add(sub)
            if commit:
                await session.commit()
                await session.refresh(sub)
            return sub
        async with self._sessionmaker() as session:
            sub = Subscription(
                organization_id=org_id,
                telegram_chat_id=tg_chat_id,
                event_type=event_type,
                student_id=student_id,
            )
            session.add(sub)
            await session.commit()
            await session.refresh(sub)
            return sub

    async def delete_subscription_by_id(
        self, sub_id: str, commit: bool = True, session: AsyncSession | None = None
    ) -> None:
        if session is not None:
            stmt = delete(Subscription).filter(Subscription.id == sub_id)
            await session.execute(stmt)
            if commit:
                await session.commit()
            return
        async with self._sessionmaker() as session:
            stmt = delete(Subscription).filter(Subscription.id == sub_id)
            await session.execute(stmt)
            await session.commit()
            return

    async def create_event(
        self,
        org_id: str,
        event_type: EventType,
        timestamp: datetime,
        student_id: str | None = None,
        camera_id: str | None = None,
        commit: bool = True,
        session: AsyncSession | None = None,
    ) -> Event:
        """Creates a new event in the system and returns the created event."""
        event = Event(
            organization_id=org_id,
            event_type=event_type,
            student_id=student_id,
            camera_id=camera_id,
            timestamp=timestamp,
        )
        if session is not None:
            session.add(event)
            if commit:
                await session.commit()
                await session.refresh(event)
            return event
        else:
            async with self._sessionmaker() as session:
                session.add(event)
                await session.commit()
                await session.refresh(event)
                return event


if TYPE_CHECKING:
    _: type[INotificationRepository] = AsyncNotificationRepository

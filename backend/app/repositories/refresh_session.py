from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_session import RefreshSession

from datetime import datetime, timezone

def create_refresh_session(
    db: Session,
    session: RefreshSession,
) -> RefreshSession:

    db.add(session)
    db.flush()
    db.refresh(session)

    return session

def get_refresh_session_by_token_hash(
    db: Session,
    token_hash: str,
) -> RefreshSession | None:

    statement = select(RefreshSession).where(
        RefreshSession.token_hash == token_hash
    )

    return db.scalar(statement)


def revoke_refresh_session(
    db: Session,
    session: RefreshSession,
) -> None:

    session.revoked_at = datetime.now(timezone.utc)
    db.flush()
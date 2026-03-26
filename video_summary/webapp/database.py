"""Database bootstrap helpers for the video-summary web application."""


from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from video_summary.webapp.models import Base


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    """Create a SQLAlchemy session factory compatible with sqlite and postgres."""
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(database_url, future=True, connect_args=connect_args)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def init_database(session_factory: sessionmaker[Session]) -> None:
    """Create the database schema for the web application if needed."""
    Base.metadata.create_all(bind=session_factory.kw["bind"])

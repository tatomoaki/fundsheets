


from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager


class PostgresDatabase:

    def __init__(self, dsn):
        self._engine = create_engine(dsn)
        self._session_factory = sessionmaker(
            bind=self._engine,
            class_=Session,
            expire_on_commit=False
        )

    @contextmanager
    def session(self) -> Generator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    def dispose(self) -> None:
        self._engine.dispose()
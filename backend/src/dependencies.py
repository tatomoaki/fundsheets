import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.storage.database import PostgresDatabase

load_dotenv()

db = PostgresDatabase(dsn=os.environ["DATABASE_URL"])

def get_db_session() -> Generator[Session, None, None]:
    with db.session() as session:
        yield session
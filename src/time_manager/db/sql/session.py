from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from time_manager.settings import DB_CONFIG
from time_manager.utils.db import get_database

engine = create_engine(get_database(DB_CONFIG).url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def session_scope(session=SessionLocal) -> Generator:
    db = session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

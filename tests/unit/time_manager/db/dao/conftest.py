import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from time_manager.db.sql.models.base import Base
from time_manager.db.sql.user import UserDao
from time_manager.schemas.user import UserDBBase
from time_manager.settings import DB_CONFIG
from time_manager.utils.db import get_database


@pytest.fixture
def session():
    engine = create_engine(get_database(DB_CONFIG).url)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield session

    Base.metadata.drop_all(engine)


@pytest.fixture
def dao(session) -> UserDao[UserDBBase]:
    return UserDao[UserDBBase](UserDBBase, session=session)

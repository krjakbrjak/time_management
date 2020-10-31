from typing import Generic, Type, TypeVar

from pydantic import BaseModel

from time_manager.db.sql.base import EntityDao
from time_manager.db.sql.models.user import User
from time_manager.db.sql.session import SessionLocal

T = TypeVar("T", bound=BaseModel)


class UserDao(EntityDao[User, T], Generic[T]):
    def __init__(self, model: Type[T], session=SessionLocal):
        super().__init__(entity=User, model=model, session=session)

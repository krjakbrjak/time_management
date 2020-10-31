from typing import Generic, Optional, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError as SqlIntegrityError

from time_manager.db import Dao
from time_manager.db.exceptions import IntegrityError, ItemNotFound
from time_manager.db.sql.models.base import Base
from time_manager.db.sql.session import SessionLocal, session_scope

Entity = TypeVar("Entity", bound=Base)
Model = TypeVar("Model", bound=BaseModel)


class EntityDao(Dao[Model], Generic[Entity, Model]):
    entity: Type[Entity]

    def __init__(self, entity: Type[Entity], model: Type[Model], session=SessionLocal):
        self.entity = entity
        self.model = model
        self.session = session

    def post(self, item: Model) -> Model:
        try:
            with session_scope(self.session) as db:
                entity = self.entity(**item.dict())  # type: ignore
                db.add(entity)
                db.flush()
                return self.model.from_orm(entity)
        except SqlIntegrityError:
            raise IntegrityError()

    def put(self, id: int, instance: Model, partial: Optional[bool] = False) -> Model:
        try:
            with session_scope(self.session) as db:
                data = instance.dict(exclude_unset=True if partial else False)
                if "id" in data:
                    del data["id"]

                if db.query(self.entity).filter_by(id=id).update(data.items()) == 0:
                    raise ItemNotFound()

                return self.model.from_orm(db.query(self.entity).get(id))
        except SqlIntegrityError:
            raise IntegrityError()

    def delete(self, id: int) -> Model:
        with session_scope(self.session) as db:
            user: Model = db.query(self.entity).get(id)
            if user:
                db.delete(user)

            return user

    def filter(
        self, skip: Optional[int] = 0, limit: Optional[int] = -1, **kwargs
    ) -> Sequence[Model]:
        with session_scope(self.session) as db:
            query = db.query(self.entity).filter_by(**kwargs).offset(skip)
            if limit and limit > -1:
                query = query.limit(limit)
            return [self.model.from_orm(e) for e in query]

import json
import os
from typing import Optional

from pydantic import BaseModel, root_validator, validator


class Sqlite(BaseModel):
    name: str
    path: str

    @validator("path")
    def validate_path(cls, value):
        if not os.path.isabs(value):
            raise ValueError("path must be absolute")

        return value

    @property
    def url(self) -> str:
        return f"sqlite:///{os.path.join(self.path, self.name)}.db"


POSTGRES_DRIVER = "psycopg2"
POSTGRES_PREFIX = "postgresql"


class Postgres(BaseModel):
    name: str
    username: str
    password: str
    host: Optional[str]
    port: Optional[int]

    @property
    def url(self) -> str:
        domain = self.host or "localhost"
        if self.port:
            domain = f"{domain}:{self.port}"
        return (
            f"{POSTGRES_PREFIX}+{POSTGRES_DRIVER}://"
            f"{self.username}:{self.password}@{domain}/{self.name}"
        )

    @validator("port")
    def validate_port(cls, value):
        if value < 1 or value > 65535:
            raise ValueError("Must be in [0, 65535]")

        return value


class Database(BaseModel):
    sqlite: Optional[Sqlite]
    postgres: Optional[Postgres]

    @property
    def url(self) -> str:
        if self.sqlite:
            return self.sqlite.url
        elif self.postgres:
            return self.postgres.url
        # This line is never reached since root_validator checks that
        # at least one of the database is specified.
        return ""

    @root_validator
    def validate_database(cls, values):
        count: int = sum(v is not None for v in values.values())
        if count != 1:
            raise ValueError("One connection must be configured")

        return values


def get_database(config_path: str) -> Database:
    with open(config_path) as config:
        return Database.parse_obj(json.loads(config.read()))

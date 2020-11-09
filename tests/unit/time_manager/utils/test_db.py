import pytest
from pydantic import ValidationError

from time_manager.utils.db import Database, Postgres, Sqlite


@pytest.mark.parametrize(
    "data, expected_result",
    [
        (
            {
                "name": "database",
                "username": "user",
                "password": "p4ss",
            },
            "postgresql+psycopg2://user:p4ss@localhost/database",
        ),
        (
            {
                "name": "database",
                "username": "user",
                "password": "p4ss",
                "port": 12,
            },
            "postgresql+psycopg2://user:p4ss@localhost:12/database",
        ),
        (
            {
                "name": "database",
                "username": "user",
                "password": "p4ss",
                "port": 12,
                "host": "q.w.e.r",
            },
            "postgresql+psycopg2://user:p4ss@q.w.e.r:12/database",
        ),
    ],
)
def test_postgres(data, expected_result):
    if expected_result:
        result = Postgres.parse_obj(data)
        assert result.url == expected_result
    else:
        with pytest.raises(ValidationError):
            Postgres.parse_obj(data)


@pytest.mark.parametrize(
    "data, expected_result",
    [({"name": "sqlite3", "path": "/aaa"}, "sqlite:////aaa/sqlite3.db")],
)
def test_sqlite(data, expected_result):
    result = Sqlite.parse_obj(data)
    assert result.url == expected_result


@pytest.mark.parametrize(
    "data, expected_result",
    [({"sqlite": {"name": "sqlite3", "path": "/aaa"}}, "sqlite:////aaa/sqlite3.db")],
)
def test_database(data, expected_result):
    result = Database.parse_obj(data)

    assert result.url == expected_result

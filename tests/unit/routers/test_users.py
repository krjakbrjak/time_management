from unittest.mock import Mock, call
from urllib.parse import urlencode

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from time_manager.db.exceptions import IntegrityError, ItemNotFound
from time_manager.main import app
from time_manager.routers.common import create_token
from time_manager.routers.users import get_user_dao
from time_manager.schemas.user import UserDB, UserDBBase
from time_manager.utils.auth import verify_password

client = TestClient(app)
client.cookies.update({"Authorization": f'Bearer {create_token("AAA")}'})


@pytest.mark.parametrize(
    "db_items", [[], [UserDB(id=1, username="ua", hashed_password="pa")]]
)
def test_get_all_users(db_items):
    dao = Mock()
    dao.filter.side_effect = [
        [UserDB(id=1, username="AAA", hashed_password="")],
        db_items,
    ]

    app.dependency_overrides[get_user_dao] = lambda: dao

    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert dao.filter.called_once
    assert dao.filter.call_args == call(**{"skip": 0, "limit": -1})

    items = [UserDBBase(**i) for i in response.json()]
    assert len(items) == len(db_items)
    if len(items):
        for i, j in zip(db_items, items):
            assert i.username == j.username


@pytest.mark.parametrize(
    "criteria, expected_status",
    [
        ({"skip": "zero", "limit": "-1.2"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"skip": 0, "limit": "-1.2"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"skip": 0, "limit": -1}, status.HTTP_200_OK),
        ({"skip": 125, "limit": 521}, status.HTTP_200_OK),
        (
            {
                "username": "",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "username": "k ",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "username": "k",
            },
            status.HTTP_200_OK,
        ),
    ],
)
def test_search_by_criteria(criteria, expected_status):
    dao = Mock()
    dao.filter.return_value = [UserDB(id=1, username="a", hashed_password="a")]

    app.dependency_overrides[get_user_dao] = lambda: dao

    ep = "/users"
    queries = urlencode(criteria)
    if queries:
        ep = f"{ep}?{queries}"

    response = client.get(ep)
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert dao.filter.called_once
        assert all(
            item in dao.filter.call_args.kwargs.items() for item in criteria.items()
        )

        items = [UserDBBase(**i) for i in response.json()][0]
        assert items.username == "a"


@pytest.mark.parametrize(
    "db_items, index, expected_status",
    [
        ([UserDB(id=1, username="ua", hashed_password="pa")], 1, status.HTTP_200_OK),
        ([], 101, status.HTTP_404_NOT_FOUND),
        ([], 6, status.HTTP_404_NOT_FOUND),
        ([], 0, status.HTTP_404_NOT_FOUND),
        ([UserDB(id=11, username="ua", hashed_password="pa")], 11, status.HTTP_200_OK),
        ([], -1, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
def test_get_users_check_indices(db_items, index, expected_status):
    dao = Mock()
    dao.filter.side_effect = [
        [UserDB(id=1, username="AAA", hashed_password="")],
        db_items,
    ]

    app.dependency_overrides[get_user_dao] = lambda: dao

    response = client.get(f"/users/{index}")
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert dao.filter.called_once
        assert dao.filter.call_args == call(**{"id": index})

        item = UserDBBase(**response.json())
        assert item.username == db_items[0].username
        assert item.id == db_items[0].id


@pytest.mark.parametrize(
    "username, password, expected_return, expected_status",
    [
        ("", "pass1", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (" ", "pass1", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("a-", "pass1", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("a j", "pass1", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("user", "pass1", IntegrityError(), status.HTTP_409_CONFLICT),
        (
            "user2",
            "pass2",
            UserDB(id=1, username="user2", hashed_password="aa"),
            status.HTTP_201_CREATED,
        ),
    ],
)
def test_create_users(username, password, expected_return, expected_status):
    dao = Mock()
    if isinstance(expected_return, Exception):
        dao.post.side_effect = expected_return
    else:
        dao.post.return_value = expected_return

    app.dependency_overrides[get_user_dao] = lambda: dao

    response = client.post("/users", json={"username": username, "password": password})
    assert dao.post.called_once
    assert response.status_code == expected_status

    if expected_status == status.HTTP_201_CREATED:
        assert verify_password(password, dao.post.call_args.args[0].hashed_password)


@pytest.mark.parametrize(
    "index, data, expected_status, expected_return",
    [
        (1, {}, status.HTTP_422_UNPROCESSABLE_ENTITY, None),
        (123, {"full_name": "FULL NAME"}, status.HTTP_422_UNPROCESSABLE_ENTITY, None),
        (
            1,
            {"id": 2, "username": "a", "hashed_password": "aaaa"},
            status.HTTP_404_NOT_FOUND,
            ItemNotFound(),
        ),
        (
            123,
            {"id": 1, "username": "a", "hashed_password": "aaaa"},
            status.HTTP_200_OK,
            UserDB(id=1, username="a", hashed_password="aaaa"),
        ),
        (
            123,
            {"id": 1, "username": "a", "hashed_password": "aaaa"},
            status.HTTP_409_CONFLICT,
            IntegrityError(),
        ),
    ],
)
def test_put_users(index, data, expected_status, expected_return):
    dao = Mock()
    dao.filter.return_value = [UserDB(id=1, username="AAA", hashed_password="")]
    if isinstance(expected_return, Exception):
        dao.put.side_effect = expected_return
    else:
        dao.put.return_value = expected_return

    app.dependency_overrides[get_user_dao] = lambda: dao

    response = client.put(f"/users/{index}", json=data)
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        user = UserDBBase(**response.json())
        assert user.username == expected_return.username
        assert user.hashed_password == expected_return.hashed_password


@pytest.mark.parametrize(
    "index, data, expected_status, expected_return",
    [
        (1, {}, status.HTTP_404_NOT_FOUND, ItemNotFound()),
        (1, {}, status.HTTP_409_CONFLICT, IntegrityError()),
        (
            1,
            {"full_name": "FULL NAME"},
            status.HTTP_200_OK,
            UserDB(id=1, username="i", hashed_password=""),
        ),
    ],
)
def test_patch_users(index, data, expected_status, expected_return):
    dao = Mock()
    dao.filter.return_value = [UserDB(id=1, username="AAA", hashed_password="")]
    if isinstance(expected_return, Exception):
        dao.put.side_effect = expected_return
    else:
        dao.put.return_value = expected_return

    app.dependency_overrides[get_user_dao] = lambda: dao

    response = client.patch(f"/users/{index}", json=data)
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        result = response.json()
        for i, j in data.items():
            if result.get(i, None):
                assert result.get(i) == j


@pytest.mark.parametrize(
    "index, expected_status, expected_return",
    [
        (-1, status.HTTP_422_UNPROCESSABLE_ENTITY, None),
        (1, status.HTTP_404_NOT_FOUND, None),
        (2, status.HTTP_200_OK, UserDB(id=2, username="n", hashed_password="")),
    ],
)
def test_delete_users(index, expected_status, expected_return):
    dao = Mock()
    dao.filter.return_value = [UserDB(id=1, username="AAA", hashed_password="")]
    if isinstance(expected_return, Exception):
        dao.delete.side_effect = expected_return
    else:
        dao.delete.return_value = expected_return

    app.dependency_overrides[get_user_dao] = lambda: dao

    response = client.delete(f"/users/{index}")
    assert response.status_code == expected_status

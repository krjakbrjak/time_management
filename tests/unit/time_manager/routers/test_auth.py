from unittest.mock import Mock

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from time_manager.main import app
from time_manager.routers.common import create_token, get_user_dao, oauth2_scheme
from time_manager.schemas.user import UserDB
from time_manager.utils.auth import get_password_hash

client: TestClient = TestClient(app)


@pytest.mark.parametrize(
    "oauth2_result, dao_result, expected_status",
    [
        (
            HTTPException(status_code=status.HTTP_401_UNAUTHORIZED),
            [],
            status.HTTP_401_UNAUTHORIZED,
        ),
        (
            create_token(username="QWERTY"),
            [UserDB(id=1, username="QWERTY", hashed_password="aaa")],
            status.HTTP_200_OK,
        ),
        ("", [], status.HTTP_401_UNAUTHORIZED),
        (create_token(username="QWERTY"), [], status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_logout(oauth2_result, dao_result, expected_status):
    app.dependency_overrides = {}
    mock_oath2_scheme = Mock()
    oauth2_throw = False
    if isinstance(oauth2_result, Exception):
        oauth2_throw = True
        mock_oath2_scheme.side_effect = oauth2_result
    else:
        mock_oath2_scheme.return_value = oauth2_result

    app.dependency_overrides[oauth2_scheme] = lambda: mock_oath2_scheme()

    dao = Mock()
    dao.filter.return_value = dao_result

    app.dependency_overrides[get_user_dao] = lambda: dao
    response = client.delete("/logout")
    assert mock_oath2_scheme.call_count == 1

    # dao.filter is called only when the token is set in either
    # a header or a cookie
    assert dao.filter.call_count == 0 if oauth2_throw else 1
    assert response.status_code == expected_status

    assert response.cookies.get("Authorization", default=None) is None


@pytest.mark.parametrize(
    "credentials, expected_result, expected_status",
    [
        ({"username": "u1", "assword": "p1"}, [], status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"username": "u1", "password": "p1"}, [], status.HTTP_401_UNAUTHORIZED),
        (
            {"username": "u1", "password": "p1"},
            [UserDB(id=1, username="u1", hashed_password=get_password_hash("p1"))],
            status.HTTP_200_OK,
        ),
    ],
)
def test_login(credentials, expected_result, expected_status):
    dao = Mock()
    dao.filter.return_value = expected_result

    app.dependency_overrides[get_user_dao] = lambda: dao

    response = client.post("/login", json=credentials)

    assert response.status_code == expected_status
    assert dao.call_count <= 1

    if dao.call_count:
        assert dao.call_args.args[0].dict() == credentials

    if expected_status == status.HTTP_200_OK:
        assert response.cookies.get("Authorization", default=None) is not None
        assert "Bearer" in response.cookies["Authorization"]

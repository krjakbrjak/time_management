import pytest
from fastapi import status

from time_manager.db.sql.base import session_scope
from time_manager.db.sql.models.user import User
from time_manager.utils.auth import get_password_hash
from time_manager.utils.client import ClientResponse, http_delete, http_post
from time_manager.utils.settings import Server


@pytest.mark.integtest
@pytest.mark.asyncio
async def test_login_logout(instance, session):
    with session_scope(session) as db:
        db.add(User(username="username", hashed_password=get_password_hash("password")))

    response: ClientResponse = await http_post(
        f"{Server.root}/login", json={"username": "username", "password": "password"}
    )

    assert response.status == status.HTTP_200_OK

    cookie = response.cookies.get("Authorization", None)
    assert cookie and cookie.value

    response = await http_delete(f"{Server.root}/logout", raise_for_status=False)
    assert response.status == status.HTTP_401_UNAUTHORIZED

    response = await http_delete(
        f"{Server.root}/logout", cookies={"Authorization": cookie.value}
    )

    assert response.status == status.HTTP_200_OK

    cookie = response.cookies.get("Authorization", None)
    assert not cookie.value

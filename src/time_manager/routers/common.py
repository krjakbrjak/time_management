from datetime import timedelta
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from time_manager.db import Dao
from time_manager.db.sql.user import UserDao
from time_manager.schemas.user import UserCredentials, UserDB
from time_manager.utils.auth import create_access_token
from time_manager.utils.auth import get_username_from_token as token_to_username
from time_manager.utils.auth import verify_password


def get_user_dao() -> UserDao[UserDB]:
    return UserDao[UserDB](UserDB)


class OAuth2PasswordBearerCookie(OAuth2PasswordBearer):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict] = None,
        auto_error: bool = True,
    ):
        super().__init__(tokenUrl, scheme_name, scopes, auto_error)

    async def __call__(
        self, request: Request, Authorization: str = Cookie("")
    ) -> Optional[str]:
        scheme, param = get_authorization_scheme_param(Authorization)

        if not Authorization or scheme.lower() != "bearer":
            return await super().__call__(request)

        return param


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="login")


def get_username_from_token(
    token: str = Depends(oauth2_scheme), db: Dao[UserDB] = Depends(get_user_dao)
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = token_to_username(token)
    if not username:
        raise credentials_exception

    if len(db.filter(username=username)) == 0:
        raise credentials_exception

    return username


def create_token(
    username: str, access_token_expires: timedelta = timedelta(minutes=60 * 3)
) -> str:
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    token: str = jsonable_encoder(access_token)
    return token


def generate_token(
    user: UserCredentials, db: Dao[UserDB] = Depends(get_user_dao)
) -> str:
    ret = db.filter(username=user.username)
    if not ret or not verify_password(user.password, ret[0].hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong credentials"
        )

    return create_token(username=user.username)

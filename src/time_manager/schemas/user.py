import re
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

USERNAME_REGEX: str = r"^[^\s-]+$"


def validate_username(value: str) -> str:
    if value is not None and not re.match(USERNAME_REGEX, value):
        raise ValueError(
            "Must not contain whitespaces/dashes and should have"
            "at least one character"
        )
    return value


class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False

    _username_validator = validator("username", allow_reuse=True)(validate_username)

    class Config:
        orm_mode = True


class UserCredentials(BaseModel):
    username: str
    password: str

    _username_validator = validator("username", allow_reuse=True)(validate_username)


class UserDBBase(UserBase):
    id: Optional[int] = None
    hashed_password: Optional[str] = None


class UserDB(UserDBBase):
    id: int
    username: str
    hashed_password: str

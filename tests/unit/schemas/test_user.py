import pytest

from time_manager.schemas.user import (
    UserBase,
    UserCredentials,
    UserDB,
    UserDBBase,
    validate_username,
)


@pytest.mark.parametrize(
    "username,should_raise",
    [
        ("", True),
        (" ", True),
        (" -", True),
        ("- ", True),
        ("-a", True),
        ("a ", True),
        ("a", False),
        ("a!@#$%^&*()_12qw", False),
        ("a !@#$%^&*()_12qw", True),
    ],
)
def test_username(username, should_raise):
    if should_raise:
        with pytest.raises(ValueError):
            validate_username(username)
    else:
        assert validate_username(username) == username


def test_models():
    UserBase()
    UserDBBase()
    UserDB(id=1, hashed_password="aa", username="user_1")
    UserCredentials(username="a", password="")
    with pytest.raises(ValueError):
        UserBase(username="")
        UserDBBase(username="")
        UserDB(id=1, hashed_password="aa", username="user 1")
        UserCredentials(username="a-b", password="")

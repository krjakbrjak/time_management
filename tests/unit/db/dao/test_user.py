import pytest

from time_manager.db.exceptions import IntegrityError, ItemNotFound
from time_manager.db.sql.base import session_scope
from time_manager.db.sql.models.user import User
from time_manager.db.sql.user import UserDao
from time_manager.schemas.user import UserDBBase


@pytest.mark.parametrize(
    "username, password",
    [
        ("user", "password"),
    ],
)
def test_user_dao_post(username, password, dao: UserDao[UserDBBase]):
    item = dao.post(item=UserDBBase(username=username, hashed_password=password))
    assert item.id is not None
    assert item.username == username
    assert item.hashed_password == password

    with pytest.raises(IntegrityError):
        item = dao.post(item=UserDBBase(username=username, hashed_password=password))


@pytest.mark.parametrize(
    "data",
    [
        [
            ("user1", "password1"),
            ("user2", "password2"),
        ]
    ],
)
def test_user_dao_filter(data, dao: UserDao[UserDBBase]):
    with session_scope(dao.session) as db:
        for username, password in data:
            db.add(User(username=username, hashed_password=password))

    items = dao.filter()

    assert len(items) == len(data)
    for (username, password), user in zip(data, items):
        assert user.id is not None
        assert user.username == username
        assert user.hashed_password == password

    items = dao.filter(skip=1)

    assert len(items) == len(data) - 1
    for (username, password), user in zip(data[1:], items):
        assert user.id is not None
        assert user.username == username
        assert user.hashed_password == password

    items = dao.filter(limit=1)

    assert len(items) == len(data) - 1
    for (username, password), user in zip(data[:1], items):
        assert user.id is not None
        assert user.username == username
        assert user.hashed_password == password

    items = dao.filter(username="1")

    assert len(items) == 0

    items = dao.filter(username=data[0][0])

    assert len(items) == 1
    assert items[0].hashed_password == data[0][1]


@pytest.mark.parametrize(
    "data",
    [
        [
            ("user1", "password1"),
            ("user2", "password2"),
        ]
    ],
)
def test_user_dao_delete(data, dao: UserDao[UserDBBase]):
    with session_scope(dao.session) as db:
        for username, password in data:
            db.add(User(username=username, hashed_password=password))

    ids = [i.id for i in dao.filter()]

    for (index, id) in enumerate(ids):
        assert id is not None
        dao.delete(id)
        assert len(dao.filter()) == len(data) - index - 1

    assert len(dao.filter()) == 0
    assert dao.delete(1) is None


@pytest.mark.parametrize(
    "data",
    [
        ("user2", "password2"),
    ],
)
def test_user_dao_put(data, dao: UserDao[UserDBBase]):
    with session_scope(dao.session) as db:
        db.add(User(username=data[0], hashed_password=data[1]))

    item = dao.filter()[0]

    assert item.id is not None

    with pytest.raises(ItemNotFound):
        dao.put(
            item.id + 1,
            UserDBBase(username=f"*{item.username}*", full_name="full_name"),
        )

    result = dao.put(
        item.id,
        UserDBBase(username=f"*{item.username}*", full_name="full_name"),
        partial=True,
    )

    assert result.username == f"*{item.username}*"
    assert result.full_name == "full_name"

    result = dao.put(
        item.id, UserDBBase(username="notpartial", hashed_password=""), partial=False
    )
    assert result.username == "notpartial"
    assert result.full_name is None

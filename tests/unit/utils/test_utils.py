import pytest

from time_manager.utils.auth import get_password_hash, verify_password


@pytest.mark.parametrize("password", ["a", "akBNKB d$4%!)(*&^", ""])
def test_password_hashing(password):
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    assert hash1 != hash2
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)
    assert not verify_password("1", hash2)
    assert not verify_password("1", hash1)


def test_hashing_argument_types():
    with pytest.raises(TypeError):
        get_password_hash(1)

    with pytest.raises(TypeError):
        get_password_hash({})

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    ret: bool = pwd_context.verify(plain_password, hashed_password)
    return ret


def get_password_hash(password: str) -> str:
    ret: str = pwd_context.hash(password)
    return ret

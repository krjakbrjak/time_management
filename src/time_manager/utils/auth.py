from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from jose.jwt import ExpiredSignatureError, JWTClaimsError, JWTError
from passlib.context import CryptContext

SECRET_KEY = "1d5a458359c2f56720d69803412c9be1e185151286d69bc3b31be91388d2f759"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    ret: bool = pwd_context.verify(plain_password, hashed_password)
    return ret


def get_password_hash(password: str) -> str:
    ret: str = pwd_context.hash(password)
    return ret


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (JWTClaimsError, JWTError, ExpiredSignatureError):
        return None


def get_username_from_token(token: str) -> Optional[str]:
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        return None

    username: str = payload.get("sub")
    return username

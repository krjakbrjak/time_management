from sqlalchemy import Boolean, Column, Integer, String

from .base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False, unique=True)
    full_name = Column(String(250), nullable=True)
    email = Column(String(), nullable=True)
    disabled = Column(Boolean, nullable=False, default=False)
    hashed_password = Column(String, nullable=False)

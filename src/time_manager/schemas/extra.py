from typing import List

from pydantic import BaseModel


class ValidationErrorModel(BaseModel):
    loc: List[str]
    msg: str
    type: str


class DetailModel(BaseModel):
    detail: List[ValidationErrorModel]


class GeneralMessage(BaseModel):
    detail: str

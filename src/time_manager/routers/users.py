from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from time_manager.db import Dao
from time_manager.db.exceptions import IntegrityError, ItemNotFound
from time_manager.routers import conflict_exception
from time_manager.routers.common import get_user_dao
from time_manager.schemas.extra import DetailModel, GeneralMessage
from time_manager.schemas.user import (
    USERNAME_REGEX,
    UserCredentials,
    UserDB,
    UserDBBase,
)
from time_manager.utils.auth import get_password_hash

router = APIRouter()


@router.post(
    "/users",
    response_model=UserDB,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": DetailModel,
            "description": "User already exists",
        }
    },
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
    name="Create user",
    operation_id="post_user",
)
def post_user(
    user: UserCredentials, db: Dao[UserDBBase] = Depends(get_user_dao)
) -> UserDBBase:
    try:
        tmp = UserDBBase(
            username=user.username,
            hashed_password=get_password_hash(user.password),
        )
        return db.post(tmp)
    except IntegrityError:
        raise conflict_exception()


@router.get(
    "/users",
    response_model=Sequence[UserDB],
    tags=["users"],
    name="Get users",
    operation_id="get_users",
)
def get_users(
    skip: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(-1, ge=-1),
    username: Optional[str] = Query(None, min_length=1, regex=USERNAME_REGEX),
    db: Dao[UserDB] = Depends(get_user_dao),
) -> Sequence[UserDB]:
    criteria = {}
    if username:
        criteria["username"] = username
    ret = db.filter(skip=skip, limit=limit, **criteria)
    return ret


@router.patch(
    "/users/{id}",
    response_model=UserDB,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": GeneralMessage,
            "description": "Item not found",
        },
        status.HTTP_409_CONFLICT: {
            "model": DetailModel,
            "description": "User already exists",
        },
    },
    tags=["user"],
    name="Update user",
    operation_id="patch_user",
)
def patch_user(
    user: UserDBBase,
    id: int = Path(..., ge=0),
    db: Dao[UserDBBase] = Depends(get_user_dao),
) -> UserDBBase:
    try:
        ret = db.put(id, user, partial=True)
        return ret
    except ItemNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found"
        )
    except IntegrityError:
        raise conflict_exception()


@router.put(
    "/users/{id}",
    response_model=UserDB,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": GeneralMessage,
            "description": "Item not found",
        },
        status.HTTP_409_CONFLICT: {
            "model": DetailModel,
            "description": "User already exists",
        },
    },
    tags=["user"],
    name="Replace user",
    operation_id="put_user",
)
def put_user(
    user: UserDB, id: int = Path(..., ge=0), db: Dao[UserDB] = Depends(get_user_dao)
) -> UserDB:
    try:
        ret = db.put(id, user, partial=True)
        return ret
    except ItemNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found"
        )
    except IntegrityError:
        raise conflict_exception()


@router.get(
    "/users/{id}",
    response_model=UserDB,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": GeneralMessage,
            "description": "Item not found",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": GeneralMessage,
            "description": "Internal server error",
        },
    },
    tags=["user"],
    name="Get user",
    operation_id="get_user_by_id",
)
def get_user_by_id(
    id: int = Path(..., ge=0), db: Dao[UserDB] = Depends(get_user_dao)
) -> UserDB:
    try:
        ret = db.filter(**{"id": id})
    except Exception:
        # Should never enter this
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    else:
        if not ret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found"
            )

        return ret[0]


@router.delete(
    "/users/{id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": GeneralMessage,
            "description": "Item not found",
        }
    },
    tags=["user"],
    status_code=status.HTTP_200_OK,
    name="Delete user",
    operation_id="delete_user",
)
def delete_user(
    id: int = Path(..., ge=0), db: Dao[UserDB] = Depends(get_user_dao)
) -> None:
    try:
        ret = db.delete(id)
    except Exception:
        # Should never enter this
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    else:
        if not ret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found"
            )

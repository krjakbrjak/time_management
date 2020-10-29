from fastapi import APIRouter, Depends, Response, status

from time_manager.routers.common import generate_token, get_username_from_token

router = APIRouter()


@router.post(
    "/login",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": str, "description": "Wrong credentials"}
    },
    status_code=status.HTTP_200_OK,
    tags=["auth"],
    name="Login",
    operation_id="login",
)
def login(response: Response, token: str = Depends(generate_token)) -> None:
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )


@router.delete(
    "/logout",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": str, "description": "Wrong credentials"}
    },
    tags=["auth"],
    name="Logout",
    operation_id="logout",
)
def logout(
    response: Response, username: str = Depends(get_username_from_token)
) -> None:
    response.delete_cookie(key="Authorization")

from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", tags=["Maintenance"], name="Ping", operation_id="ping")
async def ping():
    """
    Can be used to check if the server fully started.
    """

from fastapi import HTTPException, status

from time_manager.schemas.extra import DetailModel, ValidationErrorModel


def conflict_exception() -> HTTPException:
    error = ValidationErrorModel(
        loc=["body"], msg="Integrity error", type="storage_error.value_already_exists"
    )
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail=DetailModel(detail=[error]).dict()
    )

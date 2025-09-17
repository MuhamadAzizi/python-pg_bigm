from typing import TypeVar, Optional, Generic

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel):
    status: bool
    message: str


class ApiSuccessResponse(ApiResponse, Generic[T]):
    data: T
    meta: Optional[dict] = None


class ApiErrorResponse(ApiResponse, Generic[T]):
    errors: T
    meta: Optional[dict] = None

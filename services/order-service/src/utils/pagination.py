from typing import Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Records to skip"),
        limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    ):
        self.skip = skip
        self.limit = limit


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int

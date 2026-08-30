from typing import Generic, TypeVar

from fastapi import Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.session import Base

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int


def query_filters(request: Request) -> dict:
    skip = {"page", "page_size", "user_id"}
    return {key: value for key, value in request.query_params.items() if key not in skip}


def pagination_params(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    return {"page": page, "page_size": page_size}


def get_paginated(
    db: Session,
    model: type[Base],
    filters: dict | None = None,
    page: int = 1,
    page_size: int = 10,
    query=None,
):
    query = query if query is not None else db.query(model)
    for key, value in (filters or {}).items():
        field, op = key.split("__", 1) if "__" in key else (key, "eq")
        column = getattr(model, field)
        if op == "eq":
            query = query.filter(column == value)
        elif op == "ilike":
            query = query.filter(column.ilike(f"%{value}%"))
        elif op == "gt":
            query = query.filter(column > value)
        elif op == "lt":
            query = query.filter(column < value)
        elif op == "contains":
            query = query.filter(column.contains(value))
        else:
            raise ValueError(f"Unknown filter: {key}")
    total = query.count()
    return {
        "data": query.offset((page - 1) * page_size).limit(page_size).all(),
        "total": total,
        "page": page,
        "page_size": page_size,
    }

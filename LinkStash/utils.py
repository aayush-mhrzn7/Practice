from typing import Generic, Literal, TypeVar

from fastapi import Query, Request
from pydantic import BaseModel
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from database.session import Base

T = TypeVar("T")

LIST_QUERY_KEYS = {
    "page",
    "page_size",
    "user_id",
    "sort_dir",
    "title",
    "title__ilike",
    "title__contains",
    "id__gt",
    "id__lt",
    "tag",
    "q",
}


class Paginated(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int


def query_filters(request: Request) -> dict:
    return {key: value for key, value in request.query_params.items() if key not in LIST_QUERY_KEYS}


def list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_dir: Literal["asc", "desc"] = Query("desc"),
    title: str | None = Query(None, description="Search title or name"),
    title__ilike: str | None = Query(None),
    title__contains: str | None = Query(None),
    id__gt: int | None = Query(None),
    id__lt: int | None = Query(None),
):
    filters = {}
    if title:
        filters["title__ilike"] = title
    if title__ilike:
        filters["title__ilike"] = title__ilike
    if title__contains:
        filters["title__contains"] = title__contains
    if id__gt is not None:
        filters["id__gt"] = id__gt
    if id__lt is not None:
        filters["id__lt"] = id__lt
    return {"page": page, "page_size": page_size, "sort_dir": sort_dir, "filters": filters}


def _column(model, field: str):
    if hasattr(model, field):
        return getattr(model, field)
    if field == "title" and hasattr(model, "name"):
        return model.name
    raise ValueError(f"Unknown filter field: {field}")


def get_paginated(
    db: Session,
    model: type[Base],
    filters: dict | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_dir: Literal["asc", "desc"] = "desc",
    query=None,
):
    query = query if query is not None else db.query(model)
    for key, value in (filters or {}).items():
        if value in (None, ""):
            continue
        field, op = key.split("__", 1) if "__" in key else (key, "eq")
        column = _column(model, field)
        if op == "eq":
            query = query.filter(column == value)
        elif op == "ilike":
            query = query.filter(column.ilike(f"%{value}%"))
        elif op == "contains":
            query = query.filter(column.contains(value))
        elif op == "gt":
            query = query.filter(column > value)
        elif op == "lt":
            query = query.filter(column < value)
        elif op == "gte":
            query = query.filter(column >= value)
        elif op == "lte":
            query = query.filter(column <= value)
        elif op == "ne":
            query = query.filter(column != value)
        elif op == "startswith":
            query = query.filter(column.startswith(value))
        else:
            raise ValueError(f"Unknown filter: {key}")
    total = query.count()
    order = desc(model.id) if sort_dir == "desc" else asc(model.id)
    query = query.order_by(order)
    return {
        "data": query.offset((page - 1) * page_size).limit(page_size).all(),
        "total": total,
        "page": page,
        "page_size": page_size,
    }

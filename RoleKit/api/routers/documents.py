from api.models import Document
from api.routers.titled import make_titled_router

router = make_titled_router(
    "documents",
    Document,
    "documents:read",
    "documents:write",
    "documents:edit",
    "documents:delete",
    "Document not found",
)

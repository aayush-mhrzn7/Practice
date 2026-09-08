from api.models import Note
from api.routers.titled import make_titled_router

router = make_titled_router(
    "notes",
    Note,
    "notes:read",
    "notes:write",
    "notes:edit",
    "notes:delete",
    "Note not found",
)

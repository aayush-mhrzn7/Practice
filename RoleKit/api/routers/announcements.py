from api.models import Announcement
from api.routers.titled import make_titled_router

router = make_titled_router(
    "announcements",
    Announcement,
    "announcements:read",
    "announcements:write",
    "announcements:edit",
    "announcements:delete",
    "Announcement not found",
)

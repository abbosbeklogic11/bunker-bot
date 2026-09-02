from .lobby import router as group_lobby_router
from .admin import router as group_admin_router

__all__ = [
    "group_lobby_router",
    "group_admin_router",
]

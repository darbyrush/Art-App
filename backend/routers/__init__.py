# backend/routers/__init__.py
from .artworks import router as artworks_router
from .feedback import router as feedback_router

__all__ = ["artworks_router", "feedback_router"]
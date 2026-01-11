from fastapi import APIRouter

from .properties import router as properties_router
from .search import router as search_router

api_router = APIRouter()
api_router.include_router(properties_router, prefix="/properties", tags=["properties"])
api_router.include_router(search_router, prefix="/search", tags=["search"])

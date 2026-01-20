from fastapi import APIRouter

from app.api import auth, characters, games, scenes

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(characters.router, prefix="/characters", tags=["Characters"])
api_router.include_router(games.router, prefix="/games", tags=["Games"])
api_router.include_router(scenes.router, prefix="/scenes", tags=["Scenes"])

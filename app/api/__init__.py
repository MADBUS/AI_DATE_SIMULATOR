from fastapi import APIRouter

from app.api import auth, users, characters, games, scenes, character_settings, expressions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(characters.router, prefix="/characters", tags=["Characters"])
api_router.include_router(games.router, prefix="/games", tags=["Games"])
api_router.include_router(expressions.router, prefix="/games", tags=["Expressions"])
api_router.include_router(scenes.router, prefix="/scenes", tags=["Scenes"])
api_router.include_router(
    character_settings.router,
    prefix="/character_settings",
    tags=["Character Settings"]
)

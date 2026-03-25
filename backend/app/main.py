from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.echo import router as echo_router
from app.routers.health import router as health_router
from app.routers.items import router as items_router
from app.routers.users import router as users_router

app = FastAPI(
    title=settings.app_name,
    description="Demo FastAPI backend for frontend integration.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение модульных роутеров для более чистой архитектуры
app.include_router(health_router)
app.include_router(items_router)
app.include_router(echo_router)
app.include_router(users_router)

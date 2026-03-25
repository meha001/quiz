from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health_check() -> dict:
    # Базовая проверка, чтобы фронтенд/DevOps могли быстро понять состояние API
    return {
        "status": "ok",
        "message": "Backend is running",
        "environment": settings.app_env,
    }

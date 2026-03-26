import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from .routers import auth, creator, game, stats


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


def create_app() -> FastAPI:
    app = FastAPI(title="Quiz Platform")

    # Шаблоны и статика лежат в папке frontend, чтобы весь UI-содержимый был в одном месте
    static_dir = BASE_DIR / "frontend" / "static"
    templates_dir = BASE_DIR / "frontend" / "templates"

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    templates = Jinja2Templates(directory=str(templates_dir))

    Base.metadata.create_all(bind=engine)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(creator.router, prefix="/creator/api", tags=["creator"])
    app.include_router(game.router, prefix="/game", tags=["game"])
    app.include_router(stats.router, prefix="/stats", tags=["stats"])

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {"request": request},
        )

    @app.get("/player", response_class=HTMLResponse)
    async def player_page(request: Request):
        return templates.TemplateResponse(
            "player.html",
            {"request": request},
        )

    @app.get("/creator/login", response_class=HTMLResponse)
    async def creator_login_page(request: Request):
        return templates.TemplateResponse(
            "creator_login.html",
            {"request": request},
        )

    @app.get("/creator/dashboard", response_class=HTMLResponse)
    async def creator_dashboard_page(request: Request):
        return templates.TemplateResponse(
            "creator_dashboard.html",
            {"request": request},
        )

    @app.get("/game/{session_id}", response_class=HTMLResponse)
    async def game_page(request: Request, session_id: int):
        return templates.TemplateResponse(
            "quiz.html",
            {"request": request, "session_id": session_id},
        )

    @app.get("/results/{session_id}", response_class=HTMLResponse)
    async def results_page(request: Request, session_id: int):
        return templates.TemplateResponse(
            "results.html",
            {"request": request, "session_id": session_id},
        )

    return app


app = create_app()

import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine, ensure_sqlite_schema
from .routers import auth, creator, game, stats


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


def create_app() -> FastAPI:
    app = FastAPI(title="Quiz Platform")

    # Шаблоны и статика лежат в папке frontend, чтобы весь UI-содержимый был в одном месте
    static_dir = BASE_DIR / "frontend" / "static"
    templates_dir = BASE_DIR / "frontend" / "templates"

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    templates = Jinja2Templates(directory=str(templates_dir))

    def base_context(request: Request) -> dict:
        return {
            "request": request,
            "creator_logged_in": bool(request.cookies.get("creator_id")),
        }

    ensure_sqlite_schema()
    Base.metadata.create_all(bind=engine)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(creator.router, prefix="/creator/api", tags=["creator"])
    app.include_router(game.router, prefix="/game", tags=["game"])
    app.include_router(stats.router, prefix="/stats", tags=["stats"])

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse(request, "index.html", base_context(request))

    @app.get("/player", response_class=HTMLResponse)
    async def player_page(request: Request):
        return templates.TemplateResponse(request, "player.html", base_context(request))

    @app.get("/creator/login", response_class=HTMLResponse)
    async def creator_login_page(request: Request):
        return templates.TemplateResponse(request, "creator_login.html", base_context(request))

    @app.get("/creator/dashboard", response_class=HTMLResponse)
    async def creator_dashboard_page(request: Request):
        return templates.TemplateResponse(request, "creator_dashboard.html", base_context(request))

    @app.get("/game/{session_id}", response_class=HTMLResponse)
    async def game_page(request: Request, session_id: int):
        ctx = base_context(request)
        ctx["session_id"] = session_id
        return templates.TemplateResponse(request, "quiz.html", ctx)

    @app.get("/results/{session_id}", response_class=HTMLResponse)
    async def results_page(request: Request, session_id: int):
        ctx = base_context(request)
        ctx["session_id"] = session_id
        return templates.TemplateResponse(request, "results.html", ctx)

    # Chrome DevTools может запрашивать этот путь автоматически
    @app.get("/.well-known/appspecific/com.chrome.devtools.json")
    async def chrome_devtools_config():
        return Response(status_code=204)

    @app.get("/favicon.ico")
    async def favicon():
        return Response(status_code=204)

    return app


app = create_app()

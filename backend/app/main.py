import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
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

    def template_context(request: Request) -> dict:
        creator_logged_in = bool(request.cookies.get("creator_id"))
        return {"creator_logged_in": creator_logged_in}

    templates = Jinja2Templates(directory=str(templates_dir), context_processors=[template_context])

    Base.metadata.create_all(bind=engine)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(creator.router, prefix="/creator/api", tags=["creator"])
    app.include_router(game.router, prefix="/game", tags=["game"])
    app.include_router(stats.router, prefix="/stats", tags=["stats"])

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse(request, "index.html")

    @app.get("/player", response_class=HTMLResponse)
    async def player_page(request: Request):
        return templates.TemplateResponse(request, "player.html")

    @app.get("/creator/login", response_class=HTMLResponse)
    async def creator_login_page(request: Request):
        return templates.TemplateResponse(request, "creator_login.html")

    @app.get("/creator/dashboard", response_class=HTMLResponse)
    async def creator_dashboard_page(request: Request):
        return templates.TemplateResponse(request, "creator_dashboard.html")

    @app.get("/game/{session_id}", response_class=HTMLResponse)
    async def game_page(request: Request, session_id: int):
        return templates.TemplateResponse(request, "quiz.html", {"session_id": session_id})

    @app.get("/results/{session_id}", response_class=HTMLResponse)
    async def results_page(request: Request, session_id: int):
        return templates.TemplateResponse(request, "results.html", {"session_id": session_id})

    # Chrome DevTools может запрашивать этот путь автоматически
    @app.get("/.well-known/appspecific/com.chrome.devtools.json")
    async def chrome_devtools_config():
        return Response(status_code=204)

    @app.get("/favicon.ico")
    async def favicon():
        return Response(status_code=204)

    return app


app = create_app()

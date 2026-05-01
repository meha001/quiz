import pathlib
import tempfile
import os

from sqlalchemy import inspect, text
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
# Vercel serverless filesystem is read-only except /tmp.
# Keep local behavior with quiz.db in repo root, but switch to /tmp on Vercel.
if os.getenv("VERCEL") == "1":
    DB_PATH = pathlib.Path(tempfile.gettempdir()) / "quiz.db"
else:
    DB_PATH = BASE_DIR / "quiz.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

def ensure_sqlite_schema() -> None:
    """
    Lightweight migrations for SQLite (dev-friendly).
    Creates missing tables/columns when running with an existing quiz.db.
    """
    if not str(engine.url).startswith("sqlite"):
        return

    insp = inspect(engine)
    with engine.begin() as conn:
        tables = set(insp.get_table_names())

        if "quizzes" not in tables:
            conn.execute(
                text(
                    """
                    CREATE TABLE quizzes (
                        id INTEGER PRIMARY KEY,
                        title VARCHAR NOT NULL,
                        creator_id INTEGER NOT NULL,
                        created_at DATETIME,
                        FOREIGN KEY(creator_id) REFERENCES creators (id)
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_quizzes_creator_id ON quizzes (creator_id)"))

        # Add quiz_id to questions/sessions/highscores if missing
        def has_column(table: str, col: str) -> bool:
            return any(c["name"] == col for c in insp.get_columns(table))

        if "questions" in tables and not has_column("questions", "quiz_id"):
            conn.execute(text("ALTER TABLE questions ADD COLUMN quiz_id INTEGER"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_questions_quiz_id ON questions (quiz_id)"))

        if "sessions" in tables and not has_column("sessions", "quiz_id"):
            conn.execute(text("ALTER TABLE sessions ADD COLUMN quiz_id INTEGER"))

        if "highscores" in tables and not has_column("highscores", "quiz_id"):
            conn.execute(text("ALTER TABLE highscores ADD COLUMN quiz_id INTEGER"))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

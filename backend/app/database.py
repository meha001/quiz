import pathlib
import tempfile
import os

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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

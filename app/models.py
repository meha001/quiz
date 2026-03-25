from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="creator")
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("Creator", back_populates="user", uselist=False)


class Creator(Base):
    __tablename__ = "creators"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    reputation = Column(Float, default=0.0)
    players_passed = Column(Integer, default=0)
    avg_score = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)

    user = relationship("User", back_populates="creator")
    questions = relationship("Question", back_populates="creator")
    sessions = relationship("Session", back_populates="creator")


class QuizSettings(Base):
    __tablename__ = "quiz_settings"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"), unique=True, nullable=False)
    default_question_time = Column(Integer, nullable=False, default=30)
    questions_per_game = Column(Integer, nullable=False, default=10)
    shuffle_questions = Column(Boolean, nullable=False, default=True)

    creator = relationship("Creator", backref="settings", uselist=False)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    option_1 = Column(String, nullable=False)
    option_2 = Column(String, nullable=False)
    option_3 = Column(String, nullable=False)
    option_4 = Column(String, nullable=False)
    correct_index = Column(Integer, nullable=False)
    time_limit = Column(Integer, nullable=False, default=30)
    creator_id = Column(Integer, ForeignKey("creators.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("Creator", back_populates="questions")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("creators.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    correct_count = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    tab_switches = Column(Integer, default=0)
    failed = Column(Boolean, default=False)
    avg_answer_time = Column(Float, default=0.0)
    ip_address = Column(String, nullable=True)

    creator = relationship("Creator", back_populates="sessions")
    highscores = relationship("Highscore", back_populates="session")


class Highscore(Base):
    __tablename__ = "highscores"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    played_at = Column(DateTime, default=datetime.utcnow)
    creator_id = Column(Integer, ForeignKey("creators.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    session = relationship("Session", back_populates="highscores")


from datetime import datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import CreatorSummary, HighscoreOut, QuizOut


router = APIRouter()


@router.get("/creators", response_model=list[CreatorSummary])
def list_creators(db: Session = Depends(get_db)):
    creators = db.query(models.Creator).all()
    summaries: list[CreatorSummary] = []
    for c in creators:
        if not c.user:
            continue
        summaries.append(
            CreatorSummary(
                id=c.id,
                username=c.user.username,
                reputation=c.reputation,
                players_passed=c.players_passed,
                avg_score=c.avg_score,
            )
        )
    return summaries


@router.get("/quizzes", response_model=list[QuizOut])
def list_quizzes(db: Session = Depends(get_db)):
    # публичный список тестов
    return db.query(models.Quiz).order_by(models.Quiz.id.desc()).all()


@router.get("/creator/me/summary", response_model=CreatorSummary)
def my_creator_summary(
    creator_id: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not creator_id:
        raise HTTPException(status_code=401, detail="Требуется вход создателя")
    creator = db.query(models.Creator).filter(models.Creator.id == int(creator_id)).first()
    if not creator or not creator.user:
        raise HTTPException(status_code=404, detail="Создатель не найден")

    return CreatorSummary(
        id=creator.id,
        username=creator.user.username,
        reputation=creator.reputation,
        players_passed=creator.players_passed,
        avg_score=creator.avg_score,
    )


@router.get("/quizzes/{quiz_id}/highscores", response_model=list[HighscoreOut])
def highscores_for_quiz(
    quiz_id: int,
    period: str = Query("all", pattern="^(all|today|week)$"),
    limit: int = 10,
    db: Session = Depends(get_db),
):
    qs = db.query(models.Highscore).filter(models.Highscore.quiz_id == quiz_id)

    now = datetime.utcnow()
    if period == "today":
        start = datetime(now.year, now.month, now.day)
        qs = qs.filter(models.Highscore.played_at >= start)
    elif period == "week":
        week_ago = now - timedelta(days=7)
        qs = qs.filter(models.Highscore.played_at >= week_ago)

    highscores = qs.order_by(models.Highscore.score.desc()).limit(limit).all()
    if not highscores:
        return []

    return [HighscoreOut(player_name=h.player_name, score=h.score) for h in highscores]

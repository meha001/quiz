from datetime import datetime
import random

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import (
    GameStartRequest,
    GameStartResponse,
    GameQuestion,
    AnswerRequest,
    AnswerResponse,
    FinishResponse,
)
from ..services.reputation import recalc_creator_stats


MIN_TIME_PER_QUESTION = 3.0


router = APIRouter()


@router.post("/start", response_model=GameStartResponse)
def start_game(payload: GameStartRequest, request: Request, db: Session = Depends(get_db)):
    if payload.captcha_answer != 4:
        raise HTTPException(status_code=400, detail="Неверный ответ на проверочный пример")

    creator = db.query(models.Creator).filter(models.Creator.id == payload.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Викторина не найдена")

    questions = (
        db.query(models.Question)
        .filter(models.Question.creator_id == creator.id)
        .order_by(models.Question.created_at)
        .all()
    )
    if not questions:
        raise HTTPException(status_code=400, detail="У создателя пока нет вопросов")
    # настройки викторины
    settings = (
        db.query(models.QuizSettings)
        .filter(models.QuizSettings.creator_id == creator.id)
        .first()
    )
    if settings:
        if settings.shuffle_questions:
            random.shuffle(questions)
        if settings.questions_per_game > 0:
            questions = questions[: settings.questions_per_game]

    total_questions = len(questions)

    client_host = request.client.host if request.client else None

    session = models.Session(
        player_name=payload.player_name,
        creator_id=creator.id,
        total_questions=total_questions,
        ip_address=client_host,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    game_questions = []
    for q in questions:
        # формируем список только непустых вариантов (поддержка 2–4 ответов)
        raw_options = [q.option_1, q.option_2, q.option_3, q.option_4]
        options: list[str] = []
        for opt in raw_options:
            if opt is None:
                break
            text = opt.strip()
            if not text:
                break
            options.append(text)

        time_limit = q.time_limit
        if settings and settings.default_question_time:
            time_limit = settings.default_question_time

        game_questions.append(
            GameQuestion(
                id=q.id,
                text=q.text,
                options=options,
                time_limit=time_limit,
            )
        )

    return GameStartResponse(
        session_id=session.id,
        total_questions=total_questions,
        questions=game_questions,
    )


@router.post("/{session_id}/answer", response_model=AnswerResponse)
def submit_answer(
    session_id: int,
    payload: AnswerRequest,
    db: Session = Depends(get_db),
):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    question = db.query(models.Question).filter(models.Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    correct = payload.chosen_index == question.correct_index
    if correct:
        session.correct_count += 1

    # Накопим суммарное время, среднее посчитаем при завершении
    if payload.time_spent and payload.time_spent > 0:
        session.avg_answer_time += float(payload.time_spent)

    # Если слишком быстро — помечаем сессию как подозрительную
    if payload.time_spent < MIN_TIME_PER_QUESTION:
        session.failed = True

    db.commit()
    db.refresh(session)

    return AnswerResponse(
        correct=correct,
        correct_count=session.correct_count,
        total_questions=session.total_questions,
    )


@router.post("/{session_id}/tab-switch")
def register_tab_switch(
    session_id: int,
    db: Session = Depends(get_db),
):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    session.tab_switches += 1
    if session.tab_switches > 3:
        session.failed = True

    db.commit()
    return {"tab_switches": session.tab_switches, "failed": session.failed}


@router.post("/{session_id}/finish", response_model=FinishResponse)
def finish_game(
    session_id: int,
    db: Session = Depends(get_db),
):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    session.finished_at = datetime.utcnow()

    average_time = 0.0
    if session.total_questions > 0:
        average_time = session.avg_answer_time / float(session.total_questions)

    # финальная проверка
    if average_time < MIN_TIME_PER_QUESTION or session.tab_switches > 3:
        session.failed = True

    # добавляем в таблицу рекордов только честные игры
    if not session.failed and session.total_questions > 0:
        score = session.correct_count
        hs = models.Highscore(
            player_name=session.player_name,
            score=score,
            creator_id=session.creator_id,
            session_id=session.id,
        )
        db.add(hs)

    db.commit()

    # пересчитываем репутацию создателя
    recalc_creator_stats(db, session.creator_id)

    return FinishResponse(
        correct_count=session.correct_count,
        total_questions=session.total_questions,
        failed=session.failed,
        average_time=round(average_time, 2),
    )


from fastapi import APIRouter, Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import (
    QuestionCreate,
    QuestionUpdate,
    QuestionOut,
    QuizSettingsIn,
    QuizSettingsOut,
)


router = APIRouter()


def get_current_creator(
    creator_id: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> models.Creator:
    if not creator_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется вход создателя")
    creator = db.query(models.Creator).filter(models.Creator.id == int(creator_id)).first()
    if not creator:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Создатель не найден")
    return creator


@router.get("/questions", response_model=list[QuestionOut])
def list_questions(
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    questions = db.query(models.Question).filter(models.Question.creator_id == creator.id).all()
    return questions


@router.post("/questions", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreate,
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    # поддержка переменного числа вариантов (2–4), пустыми могут быть только последние
    raw_options = [data.option_1, data.option_2, data.option_3, data.option_4]
    options: list[str] = []
    for opt in raw_options:
        if opt is None:
            break
        text = opt.strip()
        if not text:
            break
        options.append(text)

    if len(options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Должно быть хотя бы два варианта ответа",
        )

    if data.correct_index < 0 or data.correct_index >= len(options):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Номер правильного ответа выходит за диапазон существующих вариантов",
        )

    question = models.Question(
        text=data.text,
        option_1=options[0],
        option_2=options[1] if len(options) > 1 else "",
        option_3=options[2] if len(options) > 2 else "",
        option_4=options[3] if len(options) > 3 else "",
        correct_index=data.correct_index,
        time_limit=data.time_limit,
        creator_id=creator.id,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.put("/questions/{question_id}", response_model=QuestionOut)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    question = (
        db.query(models.Question)
        .filter(models.Question.id == question_id, models.Question.creator_id == creator.id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(question, field, value)

    # пересчёт активных вариантов и валидация после обновления
    raw_options = [question.option_1, question.option_2, question.option_3, question.option_4]
    options: list[str] = []
    for opt in raw_options:
        if opt is None:
            break
        text = opt.strip()
        if not text:
            break
        options.append(text)

    if len(options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Должно быть хотя бы два варианта ответа",
        )

    if question.correct_index < 0 or question.correct_index >= len(options):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Номер правильного ответа выходит за диапазон существующих вариантов",
        )

    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    question = (
        db.query(models.Question)
        .filter(models.Question.id == question_id, models.Question.creator_id == creator.id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    db.delete(question)
    db.commit()
    return None


@router.get("/settings", response_model=QuizSettingsOut)
def get_settings(
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    settings = (
        db.query(models.QuizSettings)
        .filter(models.QuizSettings.creator_id == creator.id)
        .first()
    )
    if not settings:
        settings = models.QuizSettings(creator_id=creator.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return QuizSettingsOut(
        creator_id=settings.creator_id,
        default_question_time=settings.default_question_time,
        questions_per_game=settings.questions_per_game,
        shuffle_questions=settings.shuffle_questions,
    )


@router.put("/settings", response_model=QuizSettingsOut)
def update_settings(
    payload: QuizSettingsIn,
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    settings = (
        db.query(models.QuizSettings)
        .filter(models.QuizSettings.creator_id == creator.id)
        .first()
    )
    if not settings:
        settings = models.QuizSettings(creator_id=creator.id)
        db.add(settings)
        db.flush()

    settings.default_question_time = payload.default_question_time
    settings.questions_per_game = payload.questions_per_game
    settings.shuffle_questions = payload.shuffle_questions

    db.commit()
    db.refresh(settings)

    return QuizSettingsOut(
        creator_id=settings.creator_id,
        default_question_time=settings.default_question_time,
        questions_per_game=settings.questions_per_game,
        shuffle_questions=settings.shuffle_questions,
    )



import json

from fastapi import APIRouter, Cookie, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import (
    QuestionCreate,
    QuestionOut,
    QuestionUpdate,
    QuizCreate,
    QuizOut,
    QuizSettingsIn,
    QuizSettingsOut,
    QuizUpdate,
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
    quiz_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    qs = db.query(models.Question).filter(models.Question.creator_id == creator.id)
    if quiz_id is not None:
        qs = qs.filter(models.Question.quiz_id == quiz_id)
    questions = qs.all()
    return questions


@router.get("/quizzes", response_model=list[QuizOut])
def list_quizzes(
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    return db.query(models.Quiz).filter(models.Quiz.creator_id == creator.id).order_by(models.Quiz.id.desc()).all()


@router.post("/quizzes", response_model=QuizOut, status_code=status.HTTP_201_CREATED)
def create_quiz(
    payload: QuizCreate,
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    quiz = models.Quiz(title=payload.title, creator_id=creator.id)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


@router.put("/quizzes/{quiz_id}", response_model=QuizOut)
def update_quiz(
    quiz_id: int,
    payload: QuizUpdate,
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id, models.Quiz.creator_id == creator.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Тест не найден")
    if payload.title is not None:
        quiz.title = payload.title
    db.commit()
    db.refresh(quiz)
    return quiz


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id, models.Quiz.creator_id == creator.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Тест не найден")

    # отвяжем вопросы, чтобы не терять их (можно потом удалить вручную)
    db.query(models.Question).filter(models.Question.quiz_id == quiz.id, models.Question.creator_id == creator.id).update(
        {models.Question.quiz_id: None}
    )
    db.delete(quiz)
    db.commit()
    return None


@router.post("/quizzes/{quiz_id}/import-json", response_model=dict)
async def import_questions_json(
    quiz_id: int,
    file: UploadFile = File(...),
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    """
    JSON format example:
    {
      "title": "Optional title",
      "questions": [
        {
          "text": "Question?",
          "options": ["A", "B", "C", "D"],
          "correct_index": 1,
          "time_limit": 30
        }
      ]
    }
    """
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id, models.Quiz.creator_id == creator.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Тест не найден")

    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Не удалось прочитать JSON (нужен UTF-8)")

    if isinstance(data, dict) and data.get("title"):
        quiz.title = str(data["title"]).strip() or quiz.title

    questions = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(questions, list) or not questions:
        raise HTTPException(status_code=400, detail="В JSON должен быть массив questions")

    created = 0
    for item in questions:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", "")).strip()
        options = item.get("options", [])
        if not text or not isinstance(options, list) or len(options) < 2:
            continue
        options = [str(o).strip() for o in options if str(o).strip()]
        if len(options) < 2:
            continue

        correct_index = int(item.get("correct_index", 0))
        if correct_index < 0 or correct_index >= len(options):
            continue

        time_limit = int(item.get("time_limit", 30))
        if time_limit < 3:
            time_limit = 3

        q = models.Question(
            text=text,
            option_1=options[0],
            option_2=options[1] if len(options) > 1 else "",
            option_3=options[2] if len(options) > 2 else "",
            option_4=options[3] if len(options) > 3 else "",
            correct_index=correct_index,
            time_limit=time_limit,
            creator_id=creator.id,
            quiz_id=quiz.id,
        )
        db.add(q)
        created += 1

    db.commit()
    return {"imported": created, "quiz_id": quiz.id}


@router.post("/questions", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreate,
    creator: models.Creator = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    if data.quiz_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите тест (quiz_id), к которому относится вопрос",
        )

    quiz = (
        db.query(models.Quiz)
        .filter(models.Quiz.id == data.quiz_id, models.Quiz.creator_id == creator.id)
        .first()
    )
    if not quiz:
        raise HTTPException(status_code=404, detail="Тест не найден")

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
        quiz_id=data.quiz_id,
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
        if field == "quiz_id" and value is not None:
            quiz = (
                db.query(models.Quiz)
                .filter(models.Quiz.id == value, models.Quiz.creator_id == creator.id)
                .first()
            )
            if not quiz:
                raise HTTPException(status_code=404, detail="Тест не найден")
        setattr(question, field, value)

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

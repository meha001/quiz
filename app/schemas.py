from typing import List, Optional

from pydantic import BaseModel, constr


class CreatorRegister(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=4, max_length=100)


class CreatorLogin(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=4, max_length=100)


class CreatorPublic(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    text: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_index: int
    time_limit: int


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    option_1: Optional[str] = None
    option_2: Optional[str] = None
    option_3: Optional[str] = None
    option_4: Optional[str] = None
    correct_index: Optional[int] = None
    time_limit: Optional[int] = None


class QuestionOut(QuestionBase):
    id: int

    class Config:
        from_attributes = True


class GameStartRequest(BaseModel):
    player_name: constr(min_length=1, max_length=50)
    creator_id: int
    captcha_answer: int


class GameQuestion(BaseModel):
    id: int
    text: str
    options: List[str]
    time_limit: int


class GameStartResponse(BaseModel):
    session_id: int
    total_questions: int
    questions: List[GameQuestion]


class AnswerRequest(BaseModel):
    question_id: int
    chosen_index: int
    time_spent: float


class AnswerResponse(BaseModel):
    correct: bool
    correct_count: int
    total_questions: int


class FinishResponse(BaseModel):
    correct_count: int
    total_questions: int
    failed: bool
    average_time: float


class HighscoreOut(BaseModel):
    player_name: str
    score: int


class CreatorSummary(BaseModel):
    id: int
    username: str
    reputation: float
    players_passed: int
    avg_score: float


class QuizSettingsIn(BaseModel):
    default_question_time: int
    questions_per_game: int
    shuffle_questions: bool


class QuizSettingsOut(QuizSettingsIn):
    creator_id: int


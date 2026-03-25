from fastapi import APIRouter, Depends, HTTPException, Response, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import CreatorLogin, CreatorPublic, CreatorRegister


router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/register", response_model=CreatorPublic, status_code=status.HTTP_201_CREATED)
def register_creator(data: CreatorRegister, response: Response, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    user = models.User(
        username=data.username,
        password_hash=hash_password(data.password),
        role="creator",
    )
    db.add(user)
    db.flush()

    creator = models.Creator(id=user.id)
    db.add(creator)
    db.commit()
    db.refresh(user)

    response.set_cookie("creator_id", str(user.id), httponly=True, samesite="lax")
    return CreatorPublic(id=user.id, username=user.username)


@router.post("/login", response_model=CreatorPublic)
def login_creator(data: CreatorLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username, models.User.role == "creator").first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя или пароль")

    response.set_cookie("creator_id", str(user.id), httponly=True, samesite="lax")
    return CreatorPublic(id=user.id, username=user.username)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_creator(response: Response):
    response.delete_cookie("creator_id")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

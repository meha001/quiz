import base64
import hashlib
import hmac
import secrets

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import CreatorLogin, CreatorPublic, CreatorRegister


router = APIRouter()

_PBKDF2_ITERS = 210_000
_SALT_BYTES = 16
_DK_LEN = 32


def _pbkdf2_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERS,
        dklen=_DK_LEN,
    )


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = _pbkdf2_hash(password, salt)
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    digest_b64 = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"pbkdf2_sha256${_PBKDF2_ITERS}${salt_b64}${digest_b64}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        scheme, iters_str, salt_b64, digest_b64 = hashed_password.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iters = int(iters_str)

        def _b64decode_nopad(s: str) -> bytes:
            pad = "=" * ((4 - (len(s) % 4)) % 4)
            return base64.urlsafe_b64decode(s + pad)

        salt = _b64decode_nopad(salt_b64)
        expected = _b64decode_nopad(digest_b64)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iters,
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


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
    # Важно: удалить cookie на том же объекте Response, который возвращаем
    resp = Response(status_code=status.HTTP_204_NO_CONTENT)
    resp.delete_cookie("creator_id")
    return resp

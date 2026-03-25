from fastapi import APIRouter, HTTPException, status

from app.schemas import User, UserCreate

router = APIRouter(tags=["users"])

# Временное in-memory хранилище (имитация БД)
users_storage: dict[int, User] = {}
next_user_id = 1


@router.get("/api/users", response_model=list[User])
def list_users() -> list[User]:
    return list(users_storage.values())


@router.post("/api/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> User:
    global next_user_id

    user = User(id=next_user_id, name=payload.name, email=payload.email)
    users_storage[next_user_id] = user
    next_user_id += 1
    return user


@router.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    user = users_storage.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/api/users/{user_id}")
def delete_user(user_id: int) -> dict:
    user = users_storage.pop(user_id, None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True, "user_id": user_id}

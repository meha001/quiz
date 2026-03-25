from fastapi import APIRouter

from app.schemas import Item

router = APIRouter(tags=["items"])

_items: list[Item] = [
    Item(id=1, name="Notebook", description="A5 notebook for lecture notes", price=120),
    Item(id=2, name="Pen", description="Blue ink ballpoint pen", price=35),
    Item(id=3, name="USB Drive", description="32GB flash drive", price=450),
]


@router.get("/api/items")
def get_items() -> dict:
    # Сохраняем формат ответа совместимым с предыдущей версией
    return {"items": [item.model_dump() for item in _items]}

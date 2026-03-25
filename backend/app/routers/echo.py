from fastapi import APIRouter

from app.schemas import EchoRequest, EchoResponse

router = APIRouter(tags=["echo"])


@router.post("/api/echo", response_model=EchoResponse)
def echo_payload(payload: EchoRequest) -> EchoResponse:
    # Валидируем вход и возвращаем структурированный ответ
    return EchoResponse(
        received=True,
        echoed_message=payload.message,
        timestamp=payload.timestamp,
    )

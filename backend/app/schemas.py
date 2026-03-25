from datetime import datetime

from pydantic import BaseModel, Field


class Item(BaseModel):
    id: int
    name: str
    description: str
    price: float


class EchoRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    timestamp: datetime


class EchoResponse(BaseModel):
    received: bool
    echoed_message: str
    timestamp: datetime


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)


class User(BaseModel):
    id: int
    name: str
    email: str

#!/usr/bin/env bash
set -e

echo "[INFO] Проверка виртуального окружения..."
if [ ! -d ".venv" ]; then
  echo "[INFO] Создаем .venv"
  python3 -m venv .venv
fi

echo "[INFO] Активация .venv"
source .venv/bin/activate

echo "[INFO] Установка зависимостей"
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo "[INFO] Создаем .env из .env.example"
  cp .env.example .env
fi

echo "[INFO] Запуск FastAPI на http://127.0.0.1:8000"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

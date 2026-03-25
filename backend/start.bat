@echo off
setlocal

echo [INFO] Проверка виртуального окружения...
if not exist ".venv" (
  echo [INFO] Создаем .venv
  python -m venv .venv
)

echo [INFO] Активация .venv
call .venv\Scripts\activate.bat

echo [INFO] Установка зависимостей
pip install -r requirements.txt

if not exist ".env" (
  echo [INFO] Создаем .env из .env.example
  copy .env.example .env >nul
)

echo [INFO] Запуск FastAPI на http://127.0.0.1:8000
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

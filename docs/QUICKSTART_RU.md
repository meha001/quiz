## Быстрый запуск проекта (FastAPI + SQLite)

Проект запускается командой через `uvicorn` из корня репозитория. При старте приложение автоматически создаст SQLite БД `quiz.db` (в корне проекта), если она ещё не существует.

### 1) Проверь требования

- Python 3.10+ (`https://www.python.org/`)
- Установленный `pip`

### 2) Создай/активируй виртуальное окружение

Выполни в PowerShell **из корня проекта** (`c:\Users\Joe\OneDrive\Desktop\kontrol`):

```powershell
cd backend
python -m venv venv
.venv\Scripts\activate.bat
```

### 3) Установи зависимости

```powershell
pip install -r requirements.txt
```

### 4) Запусти сервер

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

После запуска открой в браузере:

- `http://127.0.0.1:8000/`

### 5) Где лежит база данных

- Файл SQLite: `quiz.db` (в корне проекта)
- Таблицы создаются автоматически при старте (`Base.metadata.create_all(...)` в `app/main.py`)


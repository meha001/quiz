# Quiz
Проект подготовлен для командной работы в колледже:
- `backend/` — API на FastAPI (Python)
- `frontend/` — демо-интерфейс на HTML/CSS/JS для проверки API

## Структура проекта

```text
kontrol/
├─ backend/
│  ├─ app/
│  │  ├─ routers/
│  │  │  ├─ __init__.py
│  │  │  ├─ health.py
│  │  │  ├─ items.py
│  │  │  ├─ echo.py
│  │  │  └─ users.py
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ schemas.py
│  │  └─ main.py
│  ├─ .env.example
│  ├─ main.py
│  ├─ requirements.txt
│  ├─ start.bat
│  └─ start.sh
├─ frontend/
│  ├─ index.html
│  ├─ script.js
│  └─ style.css
└─ README.md
```

## Требования

- Python `3.10+`
- `pip`

## Быстрый запуск backend

1. Перейдите в папку:
   ```bash
   cd backend
   ```

2. Запуск через скрипт:
   - Windows:
     ```bat
     start.bat
     ```
   - macOS/Linux:
     ```bash
     chmod +x start.sh
     ./start.sh
     ```

Скрипты автоматически:
- создают `.venv` (если нет),
- ставят зависимости,
- создают `.env` из `.env.example` (если нет),
- запускают FastAPI на `127.0.0.1:8000`.

## Ручной запуск backend

```bash
cd backend
python -m venv .venv
```

Windows (PowerShell):
```bash
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Запуск frontend

- Рекомендуется Live Server (порт `5500`)
- Или открыть `frontend/index.html` напрямую

## Порты

- Backend: `http://127.0.0.1:8000`
- Frontend: любой другой локальный порт (`3000`, `5500` и т.п.)

## CORS

Настраивается через переменную `CORS_ORIGINS` в `backend/.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500
```

## Структура API

| Метод | URL | Описание |
|---|---|---|
| GET | `/api/health` | Проверка состояния API |
| GET | `/api/items` | Список тестовых товаров |
| POST | `/api/echo` | Эхо-ответ с валидацией входных данных |
| GET | `/api/users` | Список пользователей |
| POST | `/api/users` | Создать пользователя |
| GET | `/api/users/{id}` | Получить пользователя по ID |
| DELETE | `/api/users/{id}` | Удалить пользователя |

## Примеры запросов

### Health
```bash
curl http://127.0.0.1:8000/api/health
```

### Items
```bash
curl http://127.0.0.1:8000/api/items
```

### Echo
```bash
curl -X POST http://127.0.0.1:8000/api/echo \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Hello API\",\"timestamp\":\"2026-03-25T10:00:00Z\"}"
```

### Users CRUD
```bash
curl http://127.0.0.1:8000/api/users
curl -X POST http://127.0.0.1:8000/api/users -H "Content-Type: application/json" -d "{\"name\":\"Ivan\",\"email\":\"ivan@example.com\"}"
curl http://127.0.0.1:8000/api/users/1
curl -X DELETE http://127.0.0.1:8000/api/users/1
```

## Скриншоты интерфейса

Добавьте скриншоты позже в этот раздел, например:
- `docs/screenshots/main.png`
- `docs/screenshots/users.png`

## Как внести свой вклад

Для одногруппников:
1. Создайте ветку: `git checkout -b feature/<short-name>`
2. Внесите изменения и проверьте работу локально
3. Убедитесь, что frontend не ломает существующие API
4. Сделайте коммит с понятным сообщением
5. Откройте Pull Request с описанием изменений

Рекомендации:
- Не менять существующие URL без обсуждения
- Для новых endpoint'ов добавлять схемы в `backend/app/schemas.py`
- Для новых групп endpoint'ов добавлять отдельный файл в `backend/app/routers/`

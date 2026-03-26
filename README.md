# Quiz Platform (FastAPI + UI)

Проект подготовлен для командной работы в колледже:
- `backend/` — backend на FastAPI (Python)
- `frontend/` — UI-файлы (Jinja2 templates + static) и отдельный demo-фронтенд для проверки API

## Структура проекта

```text
quiz/
├─ backend/
│  ├─ app/
│  │  ├─ routers/
│  │  │  ├─ __init__.py
│  │  │  ├─ auth.py
│  │  │  ├─ creator.py
│  │  │  ├─ game.py
│  │  │  └─ stats.py
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ database.py
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ services/
│  │  │  ├─ __init__.py
│  │  │  └─ reputation.py
│  │  └─ main.py
│  ├─ .env.example
│  ├─ main.py
│  ├─ requirements.txt
│  ├─ start.bat
│  └─ start.sh
├─ frontend/
│  ├─ templates/
│  ├─ static/
│  ├─ index.html          # demo-страница (проверка API)
│  ├─ script.js           # demo-скрипт (проверка API)
│  └─ style.css           # demo-стили (проверка API)
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

Открыть в браузере:
- UI (главная): `http://127.0.0.1:8000/`
- UI (игрок): `http://127.0.0.1:8000/player`
- UI (создатель): `http://127.0.0.1:8000/creator/login`
- Swagger: `http://127.0.0.1:8000/docs`

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

UI: `http://127.0.0.1:8000/`  
Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Запуск frontend

- UI викторины отдаётся backend’ом (FastAPI рендерит шаблоны из `frontend/templates` и раздаёт статику из `frontend/static`).
- Дополнительно есть demo-страница для проверки API: откройте `frontend/index.html`
  (рекомендуется через Live Server, например порт `5500`).

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
| POST | `/auth/register` | Регистрация создателя |
| POST | `/auth/login` | Вход создателя |
| POST | `/auth/logout` | Выход создателя |
| GET | `/stats/creators` | Список викторин (создателей) |
| GET | `/stats/creators/{creator_id}/highscores` | Рекорды викторины |
| GET | `/stats/creator/me/summary` | Моя статистика создателя (по cookie) |
| GET | `/creator/api/questions` | Вопросы (создатель) |
| POST | `/creator/api/questions` | Создать вопрос |
| PUT | `/creator/api/questions/{question_id}` | Обновить вопрос |
| DELETE | `/creator/api/questions/{question_id}` | Удалить вопрос |
| GET | `/creator/api/settings` | Настройки викторины |
| PUT | `/creator/api/settings` | Обновить настройки викторины |
| POST | `/game/start` | Начать игру |
| POST | `/game/{session_id}/answer` | Ответ на вопрос |
| POST | `/game/{session_id}/tab-switch` | Регистрация переключения вкладки |
| POST | `/game/{session_id}/finish` | Завершить игру |

## Примеры запросов

### Регистрация создателя
```bash
curl -X POST http://127.0.0.1:8000/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"demo\",\"password\":\"demo1234\"}"
```

### Список викторин
```bash
curl http://127.0.0.1:8000/stats/creators
```

### Старт игры
```bash
curl -X POST http://127.0.0.1:8000/game/start ^
  -H "Content-Type: application/json" ^
  -d "{\"player_name\":\"Ivan\",\"creator_id\":1,\"captcha_answer\":4}"
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

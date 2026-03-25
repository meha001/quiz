## URL проекта и устранение проблем

Это FastAPI-приложение, которое отдаёт HTML-страницы из `templates/` и статику из `static/`, а также содержит API-роуты.

## Страницы (HTML)

Открой в браузере:

- `/` — главная страница (`templates/index.html`)
- `/player` — страница игрока (`templates/player.html`)
- `/creator/login` — логин создателя (`templates/creator_login.html`)
- `/creator/dashboard` — дашборд создателя (`templates/creator_dashboard.html`)
- `/game/{session_id}` — игра по `session_id` (`templates/quiz.html`)
- `/results/{session_id}` — результаты игры (`templates/results.html`)

## API-эндпоинты

Префикс:

- API создателя: `/creator/api`
- API авторизации: `/auth`
- Игровые API: `/game`
- Статистика: `/stats`

Основные методы:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`

- `GET /creator/api/questions`
- `POST /creator/api/questions`
- `PUT /creator/api/questions/{question_id}`
- `DELETE /creator/api/questions/{question_id}`
- `GET /creator/api/settings`
- `PUT /creator/api/settings`

- `POST /game/start`
- `POST /game/{session_id}/answer`
- `POST /game/{session_id}/tab-switch`
- `POST /game/{session_id}/finish`

- `GET /stats/creators`
- `GET /stats/creator/me/summary` (использует cookie `creator_id`)
- `GET /stats/creators/{creator_id}/highscores`

## Устранение типичных проблем

### Ошибка `ValueError: password cannot be longer than 72 bytes`

Эта ошибка характерна для bcrypt и ограничения длины пароля.

Что делать:

1. Убедись, что ты запустил текущую версию кода: в `app/routers/auth.py` используется `pbkdf2_sha256` вместо bcrypt.
2. Если в `quiz.db` уже лежат пароли, захешированные по старому формату, логин может не работать. Самый простой вариант — сделать резервную копию `quiz.db` и перезаписать БД (например, удалив `quiz.db` и зарегистрировав создателя заново).

### `ModuleNotFoundError: No module named 'app'`

Запускай команду из корня проекта (`.../kontrol`), чтобы путь до `app/` был корректным.

### Порт уже занят

Если `8000` занят, поменяй параметр `--port` на свободный.


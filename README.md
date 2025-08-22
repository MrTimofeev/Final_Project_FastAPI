# Система управления проектами (MVP)

Упрощённое веб-приложение для управления командой, задачами, оценками и встречами.

## 🛠️ Стек
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- fastapi-users (JWT)
- sqladmin
- Jinja2 + Bootstrap
- Docker
- pytest

## 🚀 Установка и запуск

1. Клонируй репозиторий:
   ```bash
   git clone https://github.com/MrTimofeev/Final_Project_FastAPI.git
   cd Final_Project_FastAPI
   ```

2. Создай `.env` (на основе `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. Запусти через Docker:
   ```bash
   docker-compose up --build
   ```

4. Открой:
   - API: http://localhost:8000/docs
   - Админ: http://localhost:8000/admin
   - Фронтенд: http://localhost:8000

## 📂 Структура API

| Маршрут | Описание |
|--------|--------|
| `POST /auth/register` | Регистрация |
| `POST /auth/jwt/login` | Логин |
| `POST /teams/` | Создание команды (только admin) |
| `POST /teams/join` | Вступление по коду |
| `GET /calendar/day` | Календарь на день |

## 🧪 Тесты

```bash
pytest -v
pytest --cov=app --cov-report=html
```
Открой `htmlcov/index.html` для просмотра покрытия.

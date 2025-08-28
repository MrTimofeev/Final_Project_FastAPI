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

   Для просмотра фронтенда сначала зарегестрируйся, для этого перейди по адресу: http://localhost:8000/register и заполни форму регистрации
## 📂 Структура API

| Маршрут | Описание |
|--------|--------|
| `POST /auth/register` | Регистрация |
| `POST /auth/jwt/login` | Логин |
| `POST /team/` | Создание команды (только admin) |
| `POST /team/join` | Вступление по коду |
| `GET /calendar/day` | Календарь на день |

## 🧪 Тесты
Прежде чем запускать тесты измени в файле `.env` параметр TESTING на True.

```bash
python -m pytest -v
python -m pytest --cov=app --cov-report=term
```

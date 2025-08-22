from sqladmin import Admin, ModelView
from fastapi import FastAPI
from app.database.database import engine
from app.models.user import User
from app.models.team import Team
from app.models.task import Task
from app.models.meeting import Meeting
from app.models.evaluation import Evaluation


# Админ-панель
class UserAdmin(ModelView, model=User):
    column_list = ["id", "email", "full_name", "role", "is_active", "team"]
    column_searchable_list = ["email", "full_name"]
    column_sortable_list = ["id", "email", "role"]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class TeamAdmin(ModelView, model=Team):
    column_list = ["id", "name", "team_code", "creator"]
    column_searchable_list = ["name", "team_code"]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Команда"
    name_plural = "Команды"
    icon = "fa-solid fa-users"


class TaskAdmin(ModelView, model=Task):
    column_list = ["id", "title", "status", "creator", "assignee", "team", "deadline"]
    column_sortable_list = ["status", "deadline", "created_at"]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Задача"
    name_plural = "Задачи"
    icon = "fa-solid fa-list-check"


class MeetingAdmin(ModelView, model=Meeting):
    column_list = ["id", "title", "start_time", "end_time", "team"]
    column_sortable_list = ["start_time", "end_time"]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Встреча"
    name_plural = "Встречи"
    icon = "fa-solid fa-calendar-day"


class EvaluationAdmin(ModelView, model=Evaluation):
    column_list = ["id", "task", "user", "score", "evaluated_at"]
    column_sortable_list = ["score", "evaluated_at"]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Оценка"
    name_plural = "Оценки"
    icon = "fa-solid fa-star"


# Функция для подключения админки к FastAPI
def setup_admin(app: FastAPI):
    admin = Admin(app, engine)

    admin.add_view(UserAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(MeetingAdmin)
    admin.add_view(EvaluationAdmin)

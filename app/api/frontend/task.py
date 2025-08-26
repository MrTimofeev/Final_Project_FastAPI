from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from datetime import date, datetime

from app.core.auth import current_active_user
from app.models.user import User, RoleEnum

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/view/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, user: User = Depends(current_active_user)):
    if not user.team_id:
        request.session["messages"] = ["Сначала присоединитесь к команде."]
        return RedirectResponse("/view/teams/join", status_code=303)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/tasks/", cookies=request.cookies
            )
            if response.status_code == 200:
                tasks = response.json()
            else:
                tasks = []
                request.session["messages"] = ["Не удалось загрузить задачи."]
        except Exception as ex:
            print(ex)

            tasks = []
            request.session["messages"] = ["Сервер задач недоступен."]

    return templates.TemplateResponse(
        "tasks/list.html", {"request": request, "user": user, "tasks": tasks}
    )


@router.get("/view/tasks/create", response_class=HTMLResponse)
async def create_task_page(request: Request, user: User = Depends(current_active_user)):
    if user.role not in [RoleEnum.manager, RoleEnum.admin]:
        request.session["messages"] = [
            "Только менеджеры и администраторы могут создавать задачи."
        ]
        return RedirectResponse("/view/tasks", status_code=303)

    if not user.team_id:
        request.session["messages"] = ["Сначала присоединитесь к команде."]
        return RedirectResponse("/view/teams/join", status_code=303)

    team_members = []
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"http://localhost:8000/users/",
                params={"skip": 0, "limit": 100},
                cookies=request.cookies,
            )
            if response.status_code == 200:
                all_users = response.json()
                team_members = [u for u in all_users if u["team_id"] == user.team_id]

        except Exception:
            request.session["messages"] = ["Не удалось загрузить участников команды."]

    return templates.TemplateResponse(
        "tasks/create.html",
        {"request": request, "user": user, "team_members": team_members},
    )


@router.post("/view/tasks/create", response_class=RedirectResponse)
async def create_task_form(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    deadline: date = Form(None),
    assignee_id: int = Form(None),
    user: User = Depends(current_active_user),
):
    if user.role not in [RoleEnum.manager, RoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    if not user.team_id:
        request.session["messages"] = ["Сначала присоединитесь к команде."]
        return RedirectResponse("/teams/join", status_code=303)

    task_data = {
        "title": title,
        "description": description,
        "deadline": deadline.isoformat() if deadline else None,
        "assignee_id": assignee_id,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/tasks/", json=task_data, cookies=request.cookies
            )
            if response.status_code == 201:
                request.session["messages"] = ["Задача успешно создана!"]
                return RedirectResponse("/view/tasks", status_code=303)
            else:
                error = response.json().get("detail", "Неизвестная ошибка")
                request.session["messages"] = [f"Ошибка: {error}"]
                return RedirectResponse("/view/tasks/create", status_code=303)
        except Exception as e:
            request.session["messages"] = [f"Сервер недоступен: {str(e)}"]
            return RedirectResponse("/view/tasks/create", status_code=303)


@router.get("/view/tasks/{task_id}", response_class=HTMLResponse)
async def task_detail_page(
    request: Request, task_id: int, user: User = Depends(current_active_user)
):
    async with httpx.AsyncClient() as client:
        try:
            task_response = await client.get(
                f"http://localhost:8000/tasks/{task_id}", cookies=request.cookies
            )
            if task_response.status_code != 200:
                request.session["messages"] = ["Задача не найдена."]
                return RedirectResponse("/view/tasks", status_code=303)
            task = task_response.json()

            if isinstance(task["created_at"], str):
                task["created_at"] = datetime.fromisoformat(
                    task["created_at"].replace("Z", "+00:00")
                )

            if task["deadline"] and isinstance(task["deadline"], str):
                task["deadline"] = datetime.fromisoformat(task["deadline"]).date()

            if task["team_id"] != user.team_id:
                request.session["messages"] = ["У вас нет доступа к этой задаче."]
                return RedirectResponse("/view/tasks", status_code=303)

            creator_response = await client.get(
                f"http://localhost:8000/users/{task['creator_id']}",
                cookies=request.cookies,
            )
            creator = (
                creator_response.json()
                if creator_response.status_code == 200
                else {"email": "Unknown"}
            )

            assignee = None
            if task["assignee_id"]:
                assignee_response = await client.get(
                    f"http://localhost:8000/users/{task['assignee_id']}",
                    cookies=request.cookies,
                )
                assignee = (
                    assignee_response.json()
                    if assignee_response.status_code == 200
                    else None
                )

        except Exception as e:
            request.session["messages"] = [f"Ошибка загрузки данных: {str(e)}"]
            return RedirectResponse("/view/tasks", status_code=303)

    return templates.TemplateResponse(
        "tasks/detail.html",
        {
            "request": request,
            "user": user,
            "task": task,
            "creator": creator,
            "assignee": assignee,
        },
    )


@router.get("/view/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_page(
    request: Request, task_id: int, user: User = Depends(current_active_user)
):
    async with httpx.AsyncClient() as client:
        try:
            task_response = await client.get(
                f"http://localhost:8000/tasks/{task_id}", cookies=request.cookies
            )
            if task_response.status_code != 200:
                request.session["messages"] = ["Задача не найдена."]
                return RedirectResponse("/view/tasks", status_code=303)
            task = task_response.json()

            if isinstance(task["created_at"], str):
                task["created_at"] = datetime.fromisoformat(
                    task["created_at"].replace("Z", "+00:00")
                )

            if task["deadline"] and isinstance(task["deadline"], str):
                task["deadline"] = datetime.fromisoformat(task["deadline"]).date()

            if user.id != task["creator_id"] and user.role not in [
                RoleEnum.manager,
                RoleEnum.admin,
            ]:
                request.session["messages"] = [
                    "У вас нет прав на редактирование этой задачи."
                ]
                return RedirectResponse(f"/view/tasks/{task_id}", status_code=303)

            team_members = []
            users_response = await client.get(
                "http://localhost:8000/users/",
                params={"skip": 0, "limit": 100},
                cookies=request.cookies,
            )
            if users_response.status_code == 200:
                all_users = users_response.json()
                team_members = [u for u in all_users if u["team_id"] == user.team_id]

        except Exception as e:
            request.session["messages"] = [f"Ошибка загрузки данных: {str(e)}"]
            return RedirectResponse("/view/tasks", status_code=303)

    return templates.TemplateResponse(
        "tasks/edit.html",
        {"request": request, "user": user, "task": task, "team_members": team_members},
    )


@router.post("/view/tasks/{task_id}/edit", response_class=RedirectResponse)
async def update_task_form(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(None),
    status: str = Form(None),
    deadline: date = Form(None),
    assignee_id: int = Form(None),
    user: User = Depends(current_active_user),
):
    async with httpx.AsyncClient() as client:
        try:
            task_response = await client.get(
                f"http://localhost:8000/tasks/{task_id}", cookies=request.cookies
            )
            if task_response.status_code != 200:
                request.session["messages"] = ["Задача не найдена."]
                return RedirectResponse("/view/tasks", status_code=303)
            task = task_response.json()

            if user.id != task["creator_id"] and user.role not in [
                RoleEnum.manager,
                RoleEnum.admin,
            ]:
                request.session["messages"] = ["Нет прав на редактирование."]
                return RedirectResponse(f"/view/tasks/{task_id}", status_code=303)

            update_data = {}
            if title:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if status:
                update_data["status"] = status
            if deadline:
                update_data["deadline"] = deadline.isoformat()
            if assignee_id is not None:
                update_data["assignee_id"] = assignee_id

            response = await client.patch(
                f"http://localhost:8000/tasks/{task_id}",
                json=update_data,
                cookies=request.cookies,
            )

            if response.status_code == 200:
                request.session["messages"] = ["Задача успешно обновлена."]
            else:
                error = response.json().get("detail", "Неизвестная ошибка")
                request.session["messages"] = [f"Ошибка при сохранении: {error}"]

        except Exception as e:
            request.session["messages"] = [f"Сервер недоступен: {str(e)}"]

    return RedirectResponse(f"/view/tasks/{task_id}", status_code=303)

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx

from app.core.auth import current_active_user
from app.models.user import User, RoleEnum

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/view/evaluations/my", response_class=HTMLResponse)
async def my_evaluations_page(
    request: Request, user: User = Depends(current_active_user)
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://127.0.0.1:8000/evaluations/my", cookies=request.cookies
            )
            if response.status_code == 200:
                evaluations = response.json()
                for ev in evaluations:
                    task_response = await client.get(
                        f"http://127.0.0.1:8000/tasks/{ev['task_id']}",
                        cookies=request.cookies,
                    )
                    if task_response.status_code == 200:
                        ev["task_title"] = task_response.json()["title"]
                    else:
                        ev["task_title"] = "Задача недоступна"
            else:
                evaluations = []
                request.session["messages"] = ["Не удалось загрузить оценки."]
        except Exception as e:
            evaluations = []
            request.session["messages"] = [f"Ошибка подключения: {str(e)}"]

    return templates.TemplateResponse(
        "evaluations/my.html",
        {"request": request, "user": user, "evaluations": evaluations},
    )


# Оценки
@router.get("/view/evaluations/create", response_class=HTMLResponse)
async def create_evaluation_page(
    request: Request, user: User = Depends(current_active_user)
):
    if user.role != RoleEnum.manager:
        request.session["messages"] = ["Только менеджеры могут оценивать задачи."]
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "evaluations/create.html", {"request": request, "user": user}
    )


@router.post("/view/evaluations/create", response_class=RedirectResponse)
async def create_evaluation_form(
    request: Request,
    task_id: int = Form(...),
    score: int = Form(...),
    user: User = Depends(current_active_user),
):
    if user.role != RoleEnum.manager:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/evaluations/",
                json={"task_id": task_id, "score": score},
                cookies=request.cookies,
            )
            if response.status_code == 201:
                request.session["messages"] = ["Задача успешно оценена!"]
            else:
                error = response.json().get("detail", "Ошибка")
                request.session["messages"] = [f"Ошибка: {error}"]
        except Exception as e:
            request.session["messages"] = [f"Ошибка подключения: {e}"]

    return RedirectResponse("/view/tasks", status_code=303)

from datetime import datetime
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx

from app.core.auth import current_active_user
from app.models.user import User, RoleEnum

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/view/meetings", response_class=HTMLResponse)
async def meetings_page(request: Request, user: User = Depends(current_active_user)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/meetings/", cookies=request.cookies
            )
            if response.status_code == 200:
                meetings = response.json()
            else:
                meetings = []
                request.session["messages"] = ["Не удалось загрузить встречи."]
        except Exception:
            meetings = []
            request.session["messages"] = ["Сервер встреч недоступен."]

    return templates.TemplateResponse(
        "meetings/list.html", {"request": request, "user": user, "meetings": meetings}
    )


@router.get("/view/meetings/create", response_class=HTMLResponse)
async def create_meeting_page(
    request: Request, user: User = Depends(current_active_user)
):
    if user.role not in [RoleEnum.manager, RoleEnum.admin]:
        request.session["messages"] = [
            "Только менеджеры и администраторы могут назначать встречи."
        ]
        return RedirectResponse("/view/meetings", status_code=303)

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
        "meetings/create.html",
        {"request": request, "user": user, "team_members": team_members},
    )


@router.post("/view/meetings/create", response_class=RedirectResponse)
async def create_meeting_form(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    start_time: datetime = Form(...),
    end_time: datetime = Form(...),
    participant_ids: list[int] = Form(...),
    user: User = Depends(current_active_user),
):
    if user.role not in [RoleEnum.manager, RoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    if not user.team_id:
        request.session["messages"] = ["Сначала присоединитесь к команде."]
        return RedirectResponse("/view/teams/join", status_code=303)

    if start_time >= end_time:
        request.session["messages"] = [
            "Время начала должно быть раньше времени окончания."
        ]
        return RedirectResponse("/view/meetings/create", status_code=303)

    meeting_data = {
        "title": title,
        "description": description,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "participant_ids": participant_ids,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/meetings/",
                json=meeting_data,
                cookies=request.cookies,
            )
            if response.status_code == 201:
                request.session["messages"] = ["Встреча успешно назначена!"]
                return RedirectResponse("/view/meetings", status_code=303)
            else:
                error = response.json().get("detail", "Неизвестная ошибка")
                request.session["messages"] = [f"Ошибка: {error}"]
                return RedirectResponse("/view/meetings/create", status_code=303)
        except Exception as e:
            request.session["messages"] = [f"Сервер недоступен: {str(e)}"]
            return RedirectResponse("/view/meetings/create", status_code=303)

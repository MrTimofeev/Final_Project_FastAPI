from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx

from app.core.auth import current_active_user
from app.models.user import User, RoleEnum

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/view/teams/join", response_class=HTMLResponse)
async def join_team_page(request: Request, user: User = Depends(current_active_user)):
    if user.team_id:
        request.session["messages"] = ["Вы уже состоите в команде."]
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("teams/join.html", {"request": request, "user": user})


@router.post("/view/teams/join", response_class=RedirectResponse)
async def join_team_form(
    request: Request,
    team_code: str = Form(...),
    user: User = Depends(current_active_user),
):
    if user.team_id:
        request.session["messages"] = ["Вы уже состоите в команде."]
        return RedirectResponse("/", status_code=303)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/team/join",
                params={"team_code": team_code},
                cookies=request.cookies
            )
            if response.status_code == 200:
                request.session["messages"] = ["Вы успешно присоединились к команде!"]
                return RedirectResponse("/", status_code=303)
            else:
                error = response.json().get("detail", "Неизвестная ошибка")
                request.session["messages"] = [f"Ошибка: {error}"]
                return RedirectResponse("/view/teams/join", status_code=303)
        except Exception as e:
            request.session["messages"] = [f"Сервер недоступен: {str(e)}"]
            return RedirectResponse("/view/teams/join", status_code=303)


@router.get("/view/teams/create", response_class=HTMLResponse)
async def create_team_page(
    request: Request,
    user: User = Depends(current_active_user)
):
    if user.role != RoleEnum.admin:
        request.session["messages"] = [
            "Доступ запрещён. Только администраторы могут создавать команды."]
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("teams/create.html", {"request": request, "user": user})


@router.post("/view/teams/create", response_class=RedirectResponse)
async def create_team_form(
    request: Request,
    name: str = Form(...),
    user: User = Depends(current_active_user)
):
    if user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/team/",
                json={"name": name},
                cookies=request.cookies
            )
            if response.status_code == 201:
                data = response.json()
                request.session["messages"] = [
                    f"Команда '{data['name']}' создана! Код: {data['team_code']}"]
                return RedirectResponse("/", status_code=303)
            else:
                error = response.json().get("detail", "Неизвестная ошибка")
                request.session["messages"] = [f"Ошибка: {error}"]
                return RedirectResponse("/view/teams/create", status_code=303)
        except Exception as e:
            request.session["messages"] = [f"Сервер недоступен: {str(e)}"]
            return RedirectResponse("/view/teams/create", status_code=303)

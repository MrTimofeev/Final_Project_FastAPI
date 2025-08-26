from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

from app.core.auth import current_active_user
from app.models.user import User

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/calendar/view/day", response_class=HTMLResponse)
async def calendar_day_page(request: Request, user: User = Depends(current_active_user)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/calendar/day",
                cookies=request.cookies
            )
            if response.status_code == 200:
                data = response.json()

            else:
                data = {"date": "—", "tasks": [], "meetings": []}
                request.session["messages"] = ["Не удалось загрузить календарь."]
        except Exception:
            data = {"date": "—", "tasks": [], "meetings": []}
            request.session["messages"] = ["Ошибка подключения."]

    return templates.TemplateResponse("calendar/day.html", {
        "request": request,
        "user": user,
        "data": data
    })


@router.get("/calendar/view/month", response_class=HTMLResponse)
async def calendar_month_page(request: Request, user: User = Depends(current_active_user)):
    return templates.TemplateResponse("calendar/month.html", {"request": request, "user": user})

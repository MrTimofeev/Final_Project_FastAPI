from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx

from app.core.auth import current_active_user
from app.models.user import User

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user: User = Depends(current_active_user)):
    return templates.TemplateResponse(
        "users/profile.html", {"request": request, "user": user}
    )


@router.post("/profile/delete", response_class=RedirectResponse)
async def delete_profile(
    request: Request,
    user: User = Depends(current_active_user),
):
    """
    Удаление своего аккаунта.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"http://localhost:8000/auth/users/{user.id}", cookies=request.cookies
            )
            if response.status_code == 204:
                request.session["messages"] = ["Ваш аккаунт успешно удалён."]
                return RedirectResponse("/register", status_code=303)
            else:
                error = response.json().get("detail", "Неизвестная ошибка")
                request.session["messages"] = [f"Ошибка при удалении: {error}"]
                return RedirectResponse("/profile", status_code=303)
        except Exception as e:
            request.session["messages"] = [f"Сервер недоступен: {str(e)}"]
            return RedirectResponse("/profile", status_code=303)

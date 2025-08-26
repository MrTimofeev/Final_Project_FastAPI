from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_users import BaseUserManager

from app.core.auth import get_user_manager
from app.schemas.user import UserCreate
from app.models.user import User

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register", response_class=RedirectResponse)
async def register_user(
    request: Request,
    full_name: str = Form(None),
    email: str = Form(...),
    password: str = Form(...),
    user_manager: BaseUserManager[User, int] = Depends(get_user_manager),
):
    try:
        user_create = UserCreate(email=email, password=password, full_name=full_name)

        user = await user_manager.create(
            user_create,
            safe=True,
            request=request,
        )

        request.session["messages"] = ["Регистрация прошла успешно! Войдите в систему."]
        return RedirectResponse("/login", status_code=303)

    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            error_msg = "Пользователь с таким email уже существует"
        elif "invalid email" in error_msg.lower():
            error_msg = "Некорректный email"
        else:
            error_msg = "Ошибка регистрации: " + error_msg

        request.session["messages"] = [error_msg]
        return RedirectResponse("/register", status_code=303)

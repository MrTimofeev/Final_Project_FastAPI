from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_users import BaseUserManager
from fastapi_users.authentication.strategy import Strategy

from app.core.auth import get_user_manager, auth_backend_cookie
from app.models.user import User
from app.utils.security import verify_password

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login", response_class=RedirectResponse)
async def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    user_manager: BaseUserManager[User, int] = Depends(get_user_manager),
    strategy: Strategy = Depends(auth_backend_cookie.get_strategy),
):
    try:
        user = await user_manager.get_by_email(email)
    except Exception:
        user = None

    if not user:
        request.session["messages"] = ["Неверный email или пароль."]
        return RedirectResponse("/login", status_code=303)

    if not verify_password(password, user.hashed_password):
        request.session["messages"] = ["Неверный email или пароль."]
        return RedirectResponse("/login", status_code=303)

    if not user.is_active:
        request.session["messages"] = ["Пользователь не активен."]
        return RedirectResponse("/login", status_code=303)

    token = await strategy.write_token(user)

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key="auth",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600 * 24 * 7,
    )
    return response

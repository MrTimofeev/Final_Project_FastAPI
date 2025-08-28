from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi_users.authentication.strategy import Strategy

from app.core.auth import auth_backend_cookie

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/logout", response_class=RedirectResponse)
async def logout_route(
    request: Request,
    strategy: Strategy = Depends(auth_backend_cookie.get_strategy),
):
    response = RedirectResponse("/login", status_code=303)
    request.session.clear()
    response.delete_cookie(
        key="auth",
        path="/",
        domain=None,
        secure=False,
        httponly=True,
        samesite="lax",
    )

    request.session["messages"] = ["Вы успешно вышли."]
    return response

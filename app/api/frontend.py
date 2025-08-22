from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.auth import current_active_user
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(tags=["frontend"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: User = Depends(current_active_user)):
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "current_user": user}
    )


@router.get("/register", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(current_active_user)):
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "current_user": user}
    )


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("fastapiusersauth")
    return response

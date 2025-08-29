from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.auth import current_active_user
from app.models.user import User
from app.api.frontend import (
    login,
    register,
    evaluation,
    meeting,
    task,
    team,
    calendar,
    user,
    logout,
)

router = APIRouter(tags=["frontend"], include_in_schema=False)

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: User = Depends(current_active_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


router.include_router(user.router)
router.include_router(login.router)
router.include_router(logout.router)
router.include_router(register.router)
router.include_router(evaluation.router)
router.include_router(meeting.router)
router.include_router(task.router)
router.include_router(team.router)
router.include_router(calendar.router)

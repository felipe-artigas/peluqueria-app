# app/routers/pages.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@router.get("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html"
    )

@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html"
    )

@router.get("/404", response_class=HTMLResponse)
def not_found(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        status_code=404
    )

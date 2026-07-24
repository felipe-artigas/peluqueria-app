# app/routers/auth.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database.database import get_db
from app.schemas.administrador import AdministradorCreate, AdministradorResponse, LoginRequest, TokenResponse
from app.services import auth_service
from app.services.auth_service import obtener_admin_actual
from app.models.administrador import Administrador

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/auth", tags=["Autenticacion"])

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # Máximo 5 intentos por minuto por IP
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, login_data)

@router.post("/registro", response_model=AdministradorResponse, status_code=201)
async def registrar_admin(
    request: Request,
    admin_data: AdministradorCreate,
    db: Session = Depends(get_db),
    _=Depends(obtener_admin_actual)
):
    return auth_service.crear_administrador(db, admin_data)

@router.get("/me", response_model=AdministradorResponse)
def obtener_perfil(admin: Administrador = Depends(obtener_admin_actual)):
    return admin
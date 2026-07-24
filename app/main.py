# app/main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.routers import clientes, servicios, turnos, auth, horarios, pages, estadisticas

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de reservas para peluquerias",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Registrar el rate limiter en la app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivos estaticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Manejo global de errores
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Error de integridad en la base de datos."}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor."}
    )

# Routers
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(servicios.router)
app.include_router(turnos.router)
app.include_router(horarios.router)
app.include_router(estadisticas.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}
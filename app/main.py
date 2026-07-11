# app/main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.routers import clientes, servicios, turnos, auth, horarios, pages, estadisticas

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de reservas para peluquerias",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ============ MIDDLEWARE ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ ARCHIVOS ESTATICOS ============
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ============ MANEJO GLOBAL DE ERRORES ============
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Error de integridad en la base de datos. Verificá los datos enviados."}
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

# ============ ROUTERS ============
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(servicios.router)
app.include_router(turnos.router)
app.include_router(horarios.router)
app.include_router(estadisticas.router)

# ============ HEALTH CHECK ============
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }
# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import clientes, servicios, turnos, auth, horarios
from app.routers import clientes, servicios, turnos, auth, horarios, pages
from app.routers import clientes, servicios, turnos, auth, horarios, pages, estadisticas


app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de reservas para peluquerías",
    version="1.0.0",
    docs_url="/api/docs",      # Documentación Swagger
    redoc_url="/api/redoc"     # Documentación ReDoc
)

# CORS — permite que el frontend se comunique con el backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar el dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registrar todos los routers
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(servicios.router)
app.include_router(turnos.router)
app.include_router(horarios.router)
app.include_router(pages.router)
app.include_router(estadisticas.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
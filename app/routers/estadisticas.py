# app/routers/estadisticas.py

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import APIRouter, Depends
from app.database.database import get_db
from app.models.turno import Turno, EstadoTurno
from app.models.cliente import Cliente
from app.models.servicio import Servicio
from app.services.auth_service import obtener_admin_actual

router = APIRouter(prefix="/api/estadisticas", tags=["Estadísticas"])

@router.get("/resumen")
def obtener_resumen(
    db: Session = Depends(get_db),
    _=Depends(obtener_admin_actual)
):
    """Retorna un resumen completo de estadísticas del negocio."""
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    # Total de turnos por estado
    turnos_por_estado = {}
    for estado in EstadoTurno:
        stmt = select(func.count(Turno.id)).where(Turno.estado == estado)
        count = db.execute(stmt).scalar() or 0
        turnos_por_estado[estado.value] = count

    # Turnos de hoy
    stmt_hoy = select(func.count(Turno.id)).where(Turno.fecha == hoy)
    turnos_hoy = db.execute(stmt_hoy).scalar() or 0

    # Turnos esta semana
    stmt_semana = select(func.count(Turno.id)).where(
        Turno.fecha >= inicio_semana,
        Turno.fecha <= hoy
    )
    turnos_semana = db.execute(stmt_semana).scalar() or 0

    # Turnos este mes
    stmt_mes = select(func.count(Turno.id)).where(
        Turno.fecha >= inicio_mes,
        Turno.fecha <= hoy
    )
    turnos_mes = db.execute(stmt_mes).scalar() or 0

    # Total clientes
    stmt_clientes = select(func.count(Cliente.id)).where(Cliente.activo == True)
    total_clientes = db.execute(stmt_clientes).scalar() or 0

    # Total servicios activos
    stmt_servicios = select(func.count(Servicio.id)).where(Servicio.activo == True)
    total_servicios = db.execute(stmt_servicios).scalar() or 0

    return {
        "turnos_por_estado": turnos_por_estado,
        "turnos_hoy": turnos_hoy,
        "turnos_semana": turnos_semana,
        "turnos_mes": turnos_mes,
        "total_clientes": total_clientes,
        "total_servicios": total_servicios,
    }
# app/routers/horarios.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.database.database import get_db
from app.models.horario import Horario
from app.schemas.horario import HorarioCreate, HorarioResponse, DIAS_SEMANA
from app.services.auth_service import obtener_admin_actual

router = APIRouter(prefix="/api/horarios", tags=["Horarios"])

@router.get("/", response_model=list[HorarioResponse])
def listar_horarios(db: Session = Depends(get_db)):
    stmt = select(Horario).where(Horario.activo == True).order_by(Horario.dia_semana)
    horarios = list(db.execute(stmt).scalars().all())
    for h in horarios:
        h.dia_nombre = DIAS_SEMANA.get(h.dia_semana)
    return horarios

@router.post("/", response_model=HorarioResponse, status_code=201)
def crear_horario(
    horario_data: HorarioCreate,
    db: Session = Depends(get_db),
    _=Depends(obtener_admin_actual)
):
    # Verificar que no existe ya un horario activo para ese día
    stmt = select(Horario).where(
        Horario.dia_semana == horario_data.dia_semana,
        Horario.activo == True
    )
    existente = db.execute(stmt).scalar_one_or_none()
    if existente:
        dia_nombre = DIAS_SEMANA.get(horario_data.dia_semana, str(horario_data.dia_semana))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un horario activo para el {dia_nombre}. Eliminalo primero antes de crear uno nuevo."
        )
    horario = Horario(**horario_data.model_dump())
    db.add(horario)
    db.commit()
    db.refresh(horario)
    horario.dia_nombre = DIAS_SEMANA.get(horario.dia_semana)
    return horario

@router.delete("/{horario_id}")
def eliminar_horario(
    horario_id: int,
    db: Session = Depends(get_db),
    _=Depends(obtener_admin_actual)
):
    from datetime import date
    from app.models.turno import Turno, EstadoTurno

    stmt = select(Horario).where(Horario.id == horario_id)
    horario = db.execute(stmt).scalar_one_or_none()
    if not horario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario no encontrado"
        )

    # Verificar si hay turnos futuros activos en ese día de la semana
    hoy = date.today()
    stmt_turnos = select(Turno).where(
        Turno.fecha >= hoy,
        Turno.estado.in_([EstadoTurno.PENDIENTE, EstadoTurno.CONFIRMADO])
    )
    turnos_futuros = list(db.execute(stmt_turnos).scalars().all())

    # Filtrar los que caen en el mismo día de la semana
    dia_semana = horario.dia_semana
    turnos_en_ese_dia = [
        t for t in turnos_futuros
        if t.fecha.weekday() == dia_semana
    ]

    if turnos_en_ese_dia:
        dia_nombre = DIAS_SEMANA.get(dia_semana, str(dia_semana))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el horario del {dia_nombre} porque tiene {len(turnos_en_ese_dia)} turno(s) futuro(s) pendiente(s) o confirmado(s). Cancelalos primero."
        )

    horario.activo = False
    db.commit()
    return {"mensaje": "Horario eliminado correctamente"}
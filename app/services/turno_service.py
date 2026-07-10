# app/services/turno_service.py

from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from app.models.turno import Turno, EstadoTurno
from app.models.horario import Horario
from app.schemas.turno import TurnoCreate, TurnoUpdate

def obtener_turnos(db: Session, skip: int = 0, limit: int = 100) -> list[Turno]:
    stmt = (
        select(Turno)
        .options(joinedload(Turno.cliente), joinedload(Turno.servicio))
        .offset(skip)
        .limit(limit)
        .order_by(Turno.fecha, Turno.hora)
    )
    return list(db.execute(stmt).scalars().all())

def obtener_turno_por_id(db: Session, turno_id: int) -> Turno:
    stmt = (
        select(Turno)
        .options(joinedload(Turno.cliente), joinedload(Turno.servicio))
        .where(Turno.id == turno_id)
    )
    resultado = db.execute(stmt).scalar_one_or_none()
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turno con id {turno_id} no encontrado"
        )
    return resultado

def obtener_turnos_por_fecha(db: Session, fecha: date) -> list[Turno]:
    stmt = (
        select(Turno)
        .options(joinedload(Turno.cliente), joinedload(Turno.servicio))
        .where(
            Turno.fecha == fecha,
            Turno.estado != EstadoTurno.CANCELADO
        )
        .order_by(Turno.hora)
    )
    return list(db.execute(stmt).scalars().all())

def verificar_disponibilidad(db: Session, turno_data: TurnoCreate) -> None:
    """Verifica que no haya un turno en la misma fecha y hora."""
    stmt = select(Turno).where(
        and_(
            Turno.fecha == turno_data.fecha,
            Turno.hora == turno_data.hora,
            Turno.estado != EstadoTurno.CANCELADO
        )
    )
    turno_existente = db.execute(stmt).scalar_one_or_none()
    if turno_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un turno reservado en esa fecha y hora"
        )

def crear_turno(db: Session, turno_data: TurnoCreate) -> Turno:
    verificar_disponibilidad(db, turno_data)
    turno = Turno(**turno_data.model_dump())
    db.add(turno)
    db.commit()
    db.refresh(turno)
    return obtener_turno_por_id(db, turno.id)

def actualizar_turno(db: Session, turno_id: int, turno_data: TurnoUpdate) -> Turno:
    turno = obtener_turno_por_id(db, turno_id)
    datos = turno_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(turno, campo, valor)
    db.commit()
    db.refresh(turno)
    return obtener_turno_por_id(db, turno_id)

def cancelar_turno(db: Session, turno_id: int) -> Turno:
    turno = obtener_turno_por_id(db, turno_id)
    if turno.estado == EstadoTurno.COMPLETADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar un turno ya completado"
        )
    turno.estado = EstadoTurno.CANCELADO
    db.commit()
    return obtener_turno_por_id(db, turno_id)

def obtener_horarios_disponibles(db: Session, fecha: date, servicio_id: int) -> list[str]:
    """Retorna los horarios disponibles para una fecha y servicio específicos."""
    from datetime import time
    import app.services.servicio_service as ss

    # Obtener el día de la semana (0=Lunes)
    dia_semana = fecha.weekday()

    # Obtener horarios de atención para ese día
    stmt = select(Horario).where(
        Horario.dia_semana == dia_semana,
        Horario.activo == True
    )
    horario = db.execute(stmt).scalar_one_or_none()
    if not horario:
        return []

    # Obtener turnos ya reservados para esa fecha
    turnos_reservados = obtener_turnos_por_fecha(db, fecha)
    horas_ocupadas = {t.hora for t in turnos_reservados}

    # Generar slots de 30 minutos dentro del horario de atención
    from datetime import datetime, timedelta
    slots = []
    inicio = datetime.combine(fecha, horario.hora_inicio)
    fin = datetime.combine(fecha, horario.hora_fin)

    while inicio < fin:
        hora_actual = inicio.time()
        if hora_actual not in horas_ocupadas:
            slots.append(hora_actual.strftime("%H:%M"))
        inicio += timedelta(minutes=30)

    return slots
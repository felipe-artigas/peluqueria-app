# app/schemas/turno.py

from datetime import date, time, datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator
from app.models.turno import EstadoTurno

class TurnoBase(BaseModel):
    cliente_id: int
    servicio_id: int
    fecha: date
    hora: time
    notas: str | None = None

    @field_validator("fecha")
    @classmethod
    def validar_fecha(cls, v: date) -> date:
        from datetime import date as date_type
        if v < date_type.today():
            raise ValueError("No se pueden reservar turnos en fechas pasadas")
        return v

    @field_validator("hora")
    @classmethod
    def validar_hora(cls, v: time) -> time:
        from datetime import time as time_type
        hora_min = time_type(8, 0)
        hora_max = time_type(21, 0)
        if v < hora_min or v > hora_max:
            raise ValueError("El horario debe estar entre las 8:00 y las 21:00 hs")
        return v

    @field_validator("notas")
    @classmethod
    def validar_notas(cls, v: str | None) -> str | None:
        if v and len(v) > 500:
            raise ValueError("Las notas no pueden superar los 500 caracteres")
        return v

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    fecha: date | None = None
    hora: time | None = None
    estado: EstadoTurno | None = None
    notas: str | None = None

class ClienteResumen(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    telefono: str
    model_config = {"from_attributes": True}

class ServicioResumen(BaseModel):
    id: int
    nombre: str
    duracion: int
    precio: Decimal
    model_config = {"from_attributes": True}

class TurnoResponse(TurnoBase):
    id: int
    estado: EstadoTurno
    fecha_creacion: datetime
    cliente: ClienteResumen | None = None
    servicio: ServicioResumen | None = None
    model_config = {"from_attributes": True}
# app/schemas/servicio.py

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator

class ServicioBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    duracion: int
    precio: Decimal

    @field_validator("duracion")
    @classmethod
    def validar_duracion(cls, v: int) -> int:
        if v < 5 or v > 480:
            raise ValueError("La duracion debe estar entre 5 y 480 minutos")
        return v

    @field_validator("precio")
    @classmethod
    def validar_precio(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El precio debe ser mayor a cero")
        return v

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    duracion: int | None = None
    precio: Decimal | None = None
    activo: bool | None = None

class ServicioResponse(ServicioBase):
    id: int
    activo: bool
    fecha_creacion: datetime
    model_config = {"from_attributes": True}
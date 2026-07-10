# app/routers/clientes.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from app.services import cliente_service
from app.services.auth_service import obtener_admin_actual
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

@router.get("/", response_model=list[ClienteResponse])
def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(obtener_admin_actual)  # Ruta protegida
):
    return cliente_service.obtener_clientes(db, skip, limit)

@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_service.obtener_cliente_por_id(db, cliente_id)

@router.post("/", response_model=ClienteResponse, status_code=201)
def crear_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.crear_cliente(db, cliente_data)

@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_db),
    _=Depends(obtener_admin_actual)
):
    return cliente_service.actualizar_cliente(db, cliente_id, cliente_data)

@router.get("/buscar/email/{email}", response_model=ClienteResponse)
def buscar_por_email(email: str, db: Session = Depends(get_db)):
    """Busca un cliente por email — usado en el formulario de reserva."""
    cliente = cliente_service.obtener_cliente_por_email(db, email)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente

@router.delete("/{cliente_id}")
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _=Depends(obtener_admin_actual)
):
    return cliente_service.eliminar_cliente(db, cliente_id)
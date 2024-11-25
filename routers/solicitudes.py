from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import Solicitud, SolicitudCreate
from middlewares.auth import get_current_user
from crud import (
    create_solicitud, get_solicitud, get_solicitudes, 
    update_solicitud_status, delete_solicitud,update_solicitud_cancelado
)

router = APIRouter()

@router.post("/", response_model=Solicitud)
async def crear_solicitud(
    solicitud: SolicitudCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)):
    return await create_solicitud(db, solicitud, current_user)


@router.get("/{solicitud_id}", response_model=Solicitud)
async def obtener_solicitud(
    solicitud_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return await get_solicitud(db, solicitud_id, current_user)


@router.get("/", response_model=list[Solicitud])
async def obtener_solicitudes(
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return await get_solicitudes(db, current_user, skip=skip, limit=limit)


@router.put("/{solicitud_id}/status", response_model=Solicitud)
async def actualizar_status_solicitud(
    solicitud_id: int, 
    status: str, 
    current_user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)):
    db_solicitud = await update_solicitud_status(db, solicitud_id, status,current_user)
    if db_solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return db_solicitud



@router.put("/{solicitud_id}/cancelar", response_model=Solicitud)
async def actualizar_cancelar_solicitud(
    solicitud_id: int, 
    cancelar: bool, 
    current_user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)):
    db_solicitud = await update_solicitud_cancelado(db, solicitud_id,cancelar,current_user)
    if db_solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return db_solicitud



@router.delete("/{solicitud_id}", response_model=Solicitud)
async def eliminar_solicitud(
    solicitud_id: int, 
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)):
    db_solicitud = await delete_solicitud(db, solicitud_id,current_user)
    if db_solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return db_solicitud

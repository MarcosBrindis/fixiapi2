from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas import Historial, HistorialCreate
from crud import create_historial, get_historial, get_historiales, update_historial, delete_historial
from middlewares.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=Historial, status_code=status.HTTP_201_CREATED)
async def create_historial_endpoint(historial: HistorialCreate,current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_historial(db, historial)


@router.get("/{historial_id}", response_model=Historial)
async def read_historial(
    historial_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Obtener el historial
    db_historial = await get_historial(db, historial_id)
    if not db_historial:
        raise HTTPException(status_code=404, detail="Historial not found")
    # Verificar si el historial pertenece al cliente actual o al proveedor del servicio
    if (
        db_historial.cliente_id != current_user["user_id"] and
        (not db_historial.servicio or db_historial.servicio.proveedor_id != current_user["user_id"])
    ):
        raise HTTPException(status_code=403, detail="Not authorized to access this historial")
    return db_historial



@router.get("/", response_model=List[Historial])
async def read_historiales(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Obtener todos los historiales
    historiales = await get_historiales(db, skip=skip, limit=limit)
    if not historiales:
        raise HTTPException(status_code=404, detail="Historial not found")
    # Filtrar historiales donde el usuario es cliente o proveedor
    historiales_usuario = [
        h for h in historiales
        if h.cliente_id == current_user["user_id"] or
           (h.servicio and h.servicio.proveedor_id == current_user["user_id"])
    ]
    if not historiales_usuario:
        raise HTTPException(status_code=403, detail="No historials found for the current user")

    return historiales_usuario



@router.put("/{historial_id}", response_model=Historial)
async def update_historial_endpoint(historial_id: int, historial_data: HistorialCreate,current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_historial = await update_historial(db, historial_id, historial_data)
    if not db_historial:
        raise HTTPException(status_code=404, detail="Historial not found")
    return db_historial

@router.delete("/{historial_id}", response_model=Historial)
async def delete_historial_endpoint(
    historial_id: int,
    current_user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)):
    db_historial = await delete_historial(db, historial_id)
    if not db_historial:
        raise HTTPException(status_code=404, detail="Historial not found")
    return db_historial
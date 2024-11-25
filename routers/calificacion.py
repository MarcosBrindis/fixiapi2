from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from crud import get_calificacion, get_calificaciones, create_calificacion, update_calificacion, delete_calificacion,check_solicitud_finalizada
from schemas import CalificacionSchema, CalificacionCreateSchema
from database import get_db
from typing import List
from middlewares.auth import get_current_user

router = APIRouter()

@router.get("/{calificacion_id}", response_model=CalificacionSchema)
async def read_calificacion(
    calificacion_id: int, 
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)):
    calificacion = await get_calificacion(db, calificacion_id)
    if not calificacion:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    return calificacion

@router.get("/", response_model=List[CalificacionSchema])
async def read_calificaciones(
    skip: int = 0, limit: int = 10, 
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)):
    calificaciones = await get_calificaciones(db, skip=skip, limit=limit)
    return calificaciones



@router.post("/", response_model=CalificacionSchema)
async def create_new_calificacion(
    calificacion: CalificacionCreateSchema,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user["user_id"]  # Obtén el ID del cliente desde el token
    # Validar que exista una solicitud finalizada del usuario
    if not await check_solicitud_finalizada(db, user_id, calificacion.servicio_id):
        raise HTTPException(
            status_code=400,
            detail="El usuario no ha solicitado este servicio o el servicio no está finalizado."
        )
    # Crear la calificación y asegurarse de pasar el cliente_id
    new_calificacion = await create_calificacion(
        db, calificacion=calificacion, cliente_id=user_id
    )
    if new_calificacion.cliente_id is None:
        raise HTTPException(
            status_code=500,
            detail="Error al asignar cliente_id a la calificación."
        )
    return new_calificacion


@router.put("/{calificacion_id}", response_model=CalificacionSchema)
async def update_existing_calificacion(
    calificacion_id: int, 
    calificacion_data: CalificacionCreateSchema,
    current_user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)):
    
    db_calificacion = await get_calificacion(db, calificacion_id)
    if not db_calificacion:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    # Verificar si el usuario logueado tiene permisos
    if db_calificacion.cliente_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta calificación")
    
    updated_calificacion = await update_calificacion(db, calificacion_id, calificacion_data)
    return updated_calificacion

@router.delete("/{calificacion_id}")
async def delete_existing_calificacion(
    calificacion_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Obtener la calificación desde la base de datos
    db_calificacion = await get_calificacion(db, calificacion_id)
    if not db_calificacion:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    # Verificar si el usuario logueado tiene permisos
    if current_user["tipo_usuario"] != "Admin" and db_calificacion.cliente_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta calificación")
    # Proceder a eliminar
    await delete_calificacion(db, calificacion_id)
    return {"message": "Calificación eliminada exitosamente"}


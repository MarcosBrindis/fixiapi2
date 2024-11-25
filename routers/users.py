from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Users,Proveedor
from schemas import UserSchema, UserCreateSchema,ProveedorSchema
from typing import List  
from crud import get_user, get_users, create_user, update_user, delete_user,get_proveedor_by_user_id
from sqlalchemy.exc import SQLAlchemyError
from middlewares.auth import get_current_user


router = APIRouter()

@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    users = await get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserSchema)
async def create_new_user(user: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    new_user = await create_user(db, user)
    return new_user

@router.put("/{user_id}", response_model=UserSchema)
async def update_existing_user(
    user_id: int,
    user_data: UserCreateSchema,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    updated_user = await update_user(db, user_id, user_data)
    return updated_user


@router.delete("/{user_id}")
async def delete_existing_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Validar si el usuario tiene permisos para eliminar
    if current_user["tipo_usuario"] != "Admin" and current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete users")
    
    # Eliminar el usuario y registros relacionados
    deleted_user = await delete_user(db, user_id)
    return {"message": f"User '{deleted_user.name}' deleted successfully"}


@router.get("/users/ingresos/proveedor", response_model=dict)
async def get_proveedor_ingresos(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Validar si el usuario tiene el tipo correcto
    if current_user.get("tipo_usuario") != "Proveedor":
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta información")
    # Buscar al proveedor relacionado con el usuario logueado
    result = await db.execute(
        select(Proveedor).filter(Proveedor.user_id == current_user["user_id"])
    )
    proveedor = result.scalars().first()
    # Validar si existe el proveedor
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    # Retornar los ingresos del proveedor
    return {"ingresos": float(proveedor.ingresos)}





@router.get("/admin/ingresos/proveedores", response_model=List[ProveedorSchema])
async def get_all_proveedores_ingresos(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verificar si el usuario actual tiene permisos de administrador
    if current_user.get("tipo_usuario") != "Admin":
        raise HTTPException(
            status_code=403, detail="No tienes permiso para acceder a esta información"
        )
    # Consultar todos los ingresos de los proveedores
    result = await db.execute(select(Proveedor))
    proveedores = result.scalars().all()
    # Validar si hay proveedores
    if not proveedores:
        raise HTTPException(
            status_code=404, detail="No se encontraron proveedores en la base de datos"
        )
    # Retornar la lista de proveedores con sus ingresos
    return proveedores
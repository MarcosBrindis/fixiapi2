from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from schemas import ChatSchema, ChatCreateSchema,ChatUpdateSchema
from crud import get_chats, get_chat, create_chat, update_chat, delete_chat,get_user_chats
from database import get_db
from typing import List
from middlewares.auth import get_current_user
router = APIRouter()



# Obtener chats del usuario autenticado
@router.get("/", response_model=List[ChatSchema])
async def read_user_chats(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chats = await get_user_chats(db, user_id=current_user["user_id"], skip=skip, limit=limit)
    return chats

# Crear un nuevo chat
@router.post("/", response_model=ChatSchema)
async def create_chat_route(
    chat_data: ChatCreateSchema,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_chat = await create_chat(db, chat_data, emisor_id=current_user["user_id"])
    return new_chat

# Actualizar un chat existente
@router.put("/{chat_id}", response_model=ChatSchema)
async def update_chat_route(
    chat_id: int,
    chat_data: ChatUpdateSchema,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_chat = await update_chat(db, chat_id, chat_data, user_id=current_user["user_id"])
    if not updated_chat:
        raise HTTPException(status_code=403, detail="You can only update your own messages")
    return updated_chat

# Eliminar un chat
@router.delete("/{chat_id}")
async def delete_chat_route(
    chat_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted_chat = await delete_chat(db, chat_id, user_id=current_user["user_id"])
    if not deleted_chat:
        raise HTTPException(status_code=403, detail="You can only delete your own messages")
    return {"message": "Chat deleted successfully"}
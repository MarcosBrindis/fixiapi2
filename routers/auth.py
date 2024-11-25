from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from datetime import datetime, timedelta
from schemas import UserCreateSchema, UserLoginSchema
from database import get_db
from models import Users
from utils.security import verify_password
from sqlalchemy.future import select
from schemas import TokenResponseSchema

router = APIRouter()

SECRET_KEY = "66a106ad2e03e1443fd25f00261a1516d492d388b82d8917a4089000c6991ed6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token", response_model=TokenResponseSchema)
async def login_for_access_token(form_data: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    # Log para inspeccionar el payload recibido
    # Busca usuario en la base de datos
    user_query = await db.execute(select(Users).filter(Users.email == form_data.email))
    user = user_query.scalars().first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Genera el token con los campos permitidos
    access_token = create_access_token(data={
        "sub": str(user.user_id),
        "email": user.email,
        "tipo_usuario": user.tipo_usuario,
        "perfil_id": user.perfil_id
    })
    # Devuelve únicamente los campos necesarios
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "email": user.email,
        "tipo_usuario": user.tipo_usuario,
        "perfil_id":user.perfil_id
    }
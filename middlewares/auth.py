from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from models import Users
from database import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuración global
SECRET_KEY = "66a106ad2e03e1443fd25f00261a1516d492d388b82d8917a4089000c6991ed6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = HTTPBearer()


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload:
            raise ValueError("Invalid token payload")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

async def get_current_user(db: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    
    payload = verify_token(token.credentials)
    user_id = int(payload.get("sub"))
    email = payload.get("email")
    tipo_usuario = payload.get("tipo_usuario")
    perfil_id = payload.get("perfil_id")
    
    user_query = await db.execute(select(Users).filter(Users.user_id == user_id))
    user = user_query.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Retorna solo los datos necesarios del usuario
    return {
        "user_id": user.user_id,
        "email": email,
        "tipo_usuario": tipo_usuario,
        "perfil_id": user.perfil_id
        
    }


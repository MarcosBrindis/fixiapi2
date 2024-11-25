from pydantic import BaseModel,Field, condecimal,EmailStr
from typing import Optional, List
from datetime import datetime, time
from fastapi import UploadFile
from bson import ObjectId


class Direccion(BaseModel):
    ciudad: Optional[str]
    colonia: Optional[str]
    avenida: Optional[str]
    numexterior: Optional[int]
    codigopost: Optional[int]
 
 
# Esquema de perfil para validación de datos
class PerfilSchema(BaseModel):
    foto: Optional[bytes]
    imagenes: Optional[List[UploadFile]] = []
    description: Optional[str]
    habilidades: Optional[List[str]] = []
    telefono: Optional[str]
    direccion: Optional[dict]

    class Config:
        orm_mode = True
        
class PerfilResponseSchema(BaseModel):
    id: str
    description: Optional[str]
    habilidades: List[str]
    telefono: Optional[str]
    direccion: Optional[Direccion]
    foto: Optional[str]
    imagenes: Optional[List[str]]
    
    class Config:
        from_attributes = True

#------------------------------------

class UserSchema(BaseModel):
    user_id: int
    name: str
    email: str
    tipo_usuario: str
    fechacreate: Optional[datetime] = None
    perfil_id: Optional[str] = None

    class Config:
        from_attributes = True  # Cambiado para Pydantic v2

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    tipo_usuario: str
    perfil_id: Optional[str] = None

    class Config:
        from_attributes = True
    

class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: str
    tipo_usuario: str
    
    
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
    
class ClienteSchema(BaseModel):
    cliente_id: int
    user_id: int

    class Config:
        from_attributes = True

class ClienteCreateSchema(BaseModel):
    user_id: int

# Schema para Proveedor
class ProveedorSchema(BaseModel):
    proveedor_id: int
    user_id: int
    ingresos: float = 0
    verificado: bool = False

    class Config:
        from_attributes = True

class ProveedorCreateSchema(BaseModel):
    user_id: int
    ingresos: Optional[condecimal(gt=0)] = 0
    verificado: Optional[bool] = False

# Schema para Admin
class AdminSchema(BaseModel):
    admin_id: int
    user_id: int
    permiso_especial: bool = False

    class Config:
        from_attributes = True

class AdminCreateSchema(BaseModel):
    user_id: int
    permiso_especial: Optional[bool] = False
    
    
    
    
    
#---------------------------------------------------    
class ServicioSchema(BaseModel):
    servicio_id: int
    tipo_servicio: str
    ubicacion: str
    costo: condecimal(gt=0)
    disponibilidad: bool
    proveedor_id: int
    disponibilidadpago: bool
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class ServicioCreateSchema(BaseModel):
    tipo_servicio: str
    ubicacion: str
    costo: condecimal(gt=0)
    disponibilidad: Optional[bool] = True
    #proveedor_id: int
    disponibilidadpago: Optional[bool] = True
    descripcion: Optional[str] = None
    
#------------------------------------------------

class SolicitudBase(BaseModel):
    hora: Optional[time] = None
    servicio_id: int
    fecha_servicio: Optional[datetime] = None
class SolicitudCreate(SolicitudBase):
    pass

class Solicitud(SolicitudBase):
    solicitud_id: int
    cliente_id: int
    status: str
    fecha: datetime
    costo: condecimal(gt=0)
    cancelado:bool
    pagado:bool
    class Config:
        orm_mode = True
        
 
 #---------------------------------------------       
        
class HistorialBase(BaseModel):
    cliente_id: int
    servicio_id: int
class HistorialCreate(HistorialBase):
    pass

class Historial(HistorialBase):
    historial_id: int
    fecha: datetime

    class Config:
        orm_mode = True
        
#--------------------------------------------------

# Esquema para Dirección
class DireccionSchema(BaseModel):
    ciudad: str
    colonia: str
    avenida: str
    numexterior: int  
    codigopost: int  

    class Config:
        orm_mode = True

# Esquema para Tarjeta
class TarjetaSchema(BaseModel):
    numero: int
    nombre: str
    cvc: int

    class Config:
        orm_mode = True

# Esquema para Pago
class PagoSchema(BaseModel):
    pago_id: int
    monto: condecimal(gt=0)
    cliente_id: int
    solicitud_id: int
    direccion: DireccionSchema
    tarjeta: TarjetaSchema

    class Config:
        orm_mode = True

class PagoCreateSchema(BaseModel):
    solicitud_id: int
    direccion: DireccionSchema
    tarjeta: TarjetaSchema
    class Config:
        orm_mode = True
        
#----------------------------------
class CalificacionSchema(BaseModel):
    calificacion_id: int
    puntuaje: int
    reseña: Optional[str] = None
    fecha: datetime
    cliente_id: int
    servicio_id: int

    class Config:
        from_attributes = True

class CalificacionCreateSchema(BaseModel):
    puntuaje: int
    reseña: Optional[str] = None
    servicio_id: int
    
#-------------------------------------
class ChatSchema(BaseModel):
    chat_id: int
    mensaje: str
    fechacreate: datetime
    resepto_id: int
    emisor_id: int

    class Config:
        from_attributes = True

class ChatCreateSchema(BaseModel):
    mensaje: str
    resepto_id: int

class ChatUpdateSchema(BaseModel):
    mensaje: str

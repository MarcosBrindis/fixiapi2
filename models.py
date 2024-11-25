from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, JSON, Boolean, DECIMAL, TIMESTAMP, ARRAY,DateTime,Time,TEXT,LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from sqlalchemy.sql import func
from decimal import Decimal
from sqlalchemy import LargeBinary
Base = declarative_base()
from models import Base  
from sqlalchemy.types import TypeDecorator
import json
from pydantic import BaseModel
from typing import List, Optional,Dict, Any
from bson import Binary,ObjectId


class status(str, enum.Enum):
    PENDIENTE = 'PENDIENTE'
    ACEPTADO = 'ACEPTADO'
    RECHAZADO = 'RECHAZADO'
    FINALIZADO = 'FINALIZADO'


class PydanticObjectId(str):  
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise ValueError("Invalid ObjectId")
        return str(v)  # Lo convertimos a string para que sea compatible con Pydantic


class PerfilModel(BaseModel):
    id: Optional[PydanticObjectId] = None  
    foto: Optional[bytes  ]  
    description: Optional[str]
    habilidades: Optional[List[str]] = []  
    telefono: Optional[str] = None
    direccion: Optional[dict] = None  # direccion guardada como un diccionario
    imagenes: Optional[List[bytes]] = []
    class Config:
        from_attributes = True  # Usa 'from_attributes' en lugar de 'orm_mode'
        str_strip_whitespace = True  # Elimina los espacios en blanco al inicio y final
        str_min_length = 1  # Asegura que las cadenas no sean vacías




class perfil(Base):
    __tablename__ = 'perfil'

    perfil_id = Column(Integer, primary_key=True, index=True)
    foto = Column(LargeBinary) 
    description = Column(Text)
    habilidades = Column(ARRAY(String))
    telefono = Column(String(20))
    direccion = Column(JSON)



class Users(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    fechacreate = Column(TIMESTAMP, server_default=func.now())
    tipo_usuario = Column(String(20), nullable=False)
    perfil_id = Column(String, nullable=True)
    cliente = relationship("Cliente", back_populates="user", uselist=False)
    proveedor = relationship("Proveedor", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)
    servicios = relationship("Servicio", back_populates="proveedor")
    solicitudes = relationship("Solicitud", back_populates="cliente")
    calificaciones = relationship("Calificacion", back_populates="cliente")
    historial = relationship("Historial", back_populates="cliente")
   # pagos = relationship("pagos", back_populates="cliente")

class Cliente(Base):
    __tablename__ = 'cliente'
    
    cliente_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)

    user = relationship("Users", back_populates="cliente")



class Proveedor(Base):
    __tablename__ = 'proveedor'
    
    proveedor_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    ingresos = Column(DECIMAL, default=0)
    verificado = Column(Boolean, default=False)

    user = relationship("Users", back_populates="proveedor")
    

class Admin(Base):
    __tablename__ = 'admin'
    
    admin_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    permiso_especial = Column(Boolean, default=False)

    user = relationship("Users", back_populates="admin")

class Servicio(Base):
    __tablename__ = 'servicio'

    servicio_id = Column(Integer, primary_key=True, index=True)
    tipo_servicio = Column(String(100), nullable=False)
    ubicacion = Column(String(100), nullable=False)
    costo = Column(DECIMAL, nullable=False)
    disponibilidad = Column(Boolean, default=True)
    proveedor_id = Column(Integer, ForeignKey("users.user_id"))
    disponibilidadpago = Column(Boolean, default=True)
    descripcion=Column(Text)
    proveedor = relationship("Users", back_populates="servicios")
    calificaciones = relationship('Calificacion', back_populates='servicio')
    

class Solicitud(Base):
    __tablename__ = "solicitud"
    
    solicitud_id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(status), default=status.PENDIENTE)
    fecha = Column(TIMESTAMP(timezone=True), server_default=func.now())
    hora = Column(Time)
    costo = Column(DECIMAL)
    fecha_servicio = Column(TIMESTAMP)
    cliente_id = Column(Integer, ForeignKey("users.user_id"))
    servicio_id = Column(Integer, ForeignKey("servicio.servicio_id"))
    cancelado = Column(Boolean, default=False)
    pagado = Column(Boolean, default=False)
    cliente = relationship("Users", back_populates="solicitudes")
    servicio = relationship("Servicio")


class Historial(Base):
    __tablename__ = "historial"

    historial_id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    cliente_id = Column(Integer, ForeignKey("users.user_id"))
    servicio_id = Column(Integer, ForeignKey("servicio.servicio_id"), nullable=True)

    cliente = relationship("Users", back_populates="historial")
    servicio = relationship("Servicio")



class Pago(Base):
    __tablename__ = 'pagos'

    pago_id = Column(Integer, primary_key=True, index=True)
    monto = Column(DECIMAL, nullable=False)
    cliente_id = Column(Integer, ForeignKey("users.user_id"))
    solicitud_id = Column(Integer, ForeignKey("solicitud.solicitud_id"))
    direccion = Column(JSON)  # Se eliminó la coma innecesaria
    tarjeta = Column(JSON)  # Se eliminó la coma innecesaria
    solicitud = relationship("Solicitud")
    


class Calificacion(Base):
    __tablename__ = 'calificacion'

    calificacion_id = Column(Integer, primary_key=True, index=True)
    puntuaje = Column(Integer, nullable=False)
    reseña = Column(Text, nullable=True)
    fecha = Column(TIMESTAMP, default=func.current_timestamp())
    cliente_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    servicio_id = Column(Integer, ForeignKey('servicio.servicio_id'), nullable=False)

    cliente = relationship('Users', back_populates='calificaciones')
    servicio = relationship('Servicio', back_populates='calificaciones')
    

class Chat(Base):
    __tablename__ = 'chat'

    chat_id = Column(Integer, primary_key=True, index=True)
    mensaje = Column(Text, nullable=False)
    fechacreate = Column(TIMESTAMP, server_default=func.now())
    resepto_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    emisor_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    proveedor = relationship("Users", foreign_keys=[resepto_id])
    cliente = relationship("Users", foreign_keys=[emisor_id])
    
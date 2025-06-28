from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class EstadoRetroalimentacion(str, Enum):
    PENDIENTE = 'Pendiente'
    RESUELTA = 'Resuelta'

class Retroalimentacion(Base):
    __tablename__ = 'retroalimentacion'

    idretroalimentacion = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)
    mensaje = Column(String(1000), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    estado = Column(Enum(EstadoRetroalimentacion), default=EstadoRetroalimentacion.PENDIENTE)
    idmedico = Column(Integer, ForeignKey('medico.idmedico'), nullable=False)
    
    medico = relationship('Medico', back_populates='retroalimentaciones')

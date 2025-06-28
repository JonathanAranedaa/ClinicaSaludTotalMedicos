from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime

class Retroalimentacion(Base):
    __tablename__ = 'retroalimentaciones'
    
    id_retroalimentacion = Column(Integer, primary_key=True)
    tipo = Column(String(30), nullable=False, default='Sugerencia')
    mensaje = Column(String(1000), nullable=False)
    fecha = Column(DateTime, nullable=False, default=datetime.now)
    estado = Column(String(50), nullable=False, default='Pendiente')  # Pendiente, Completado
    id_medico = Column(Integer, ForeignKey('medicos.id_medico'), nullable=False)
    
    # Relaciones
    medico = relationship('Medico', backref='retroalimentaciones')
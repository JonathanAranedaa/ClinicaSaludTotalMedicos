from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Time, TIMESTAMP
from sqlalchemy.orm import relationship
from app.models.base import Base

class Horario(Base):
    __tablename__ = 'horarios'
    
    id_horario = Column(Integer, primary_key=True)
    id_medico = Column(Integer, ForeignKey('medicos.id_medico'), nullable=False)
    dia_semana = Column(String(10), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_salida = Column(Time, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    
    # Relaciones
    medico = relationship('Medico', backref='horarios')

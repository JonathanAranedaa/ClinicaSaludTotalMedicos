from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

# Definir las clases en orden dependiente
class Medico(Base):
    __tablename__ = 'medico'
    
    id_medico = Column(Integer, primary_key=True)
    certificacion = Column(String(200), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    id_especialidad = Column(Integer, ForeignKey('especialidades.id_especialidad'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    
    especialidad = relationship('Especialidades', backref='medicos')
    usuario = relationship('User', backref='medico')
    horarios = relationship('Horario', back_populates='medico', cascade='all, delete-orphan')
    retroalimentaciones = relationship('Retroalimentacion', back_populates='medico')
    
    def __repr__(self):
        return f"<Medico {self.certificacion}>"

class Retroalimentacion(Base):
    __tablename__ = 'retroalimentacion'

    id_retroalimentacion = Column(Integer, primary_key=True)
    id_medico = Column(Integer, ForeignKey('medicos.id_medico'), nullable=False)
    tipo = Column(String(30), nullable=False, default='Sugerencia')
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    estado = Column(String(20), nullable=False, default='Pendiente')
    mensaje = Column(String(1000), nullable=False)
    
    medico = relationship('Medico', back_populates='retroalimentaciones')

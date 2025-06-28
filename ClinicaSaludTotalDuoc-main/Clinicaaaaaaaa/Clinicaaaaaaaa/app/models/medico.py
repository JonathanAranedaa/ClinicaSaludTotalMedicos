from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Medico(Base):
    __tablename__ = 'medicos'
    
    id_medico = Column(Integer, Base.generate_id('medicos'), primary_key=True)
    certificacion = Column(String(200), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    id_especialidad = Column(Integer, ForeignKey('especialidades.id_especialidad'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    
    # Relaciones
    usuario = relationship('User', backref='medico')
    especialidad = relationship('Especialidades', backref='medicos')

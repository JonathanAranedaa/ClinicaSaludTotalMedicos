from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, TIMESTAMP
from sqlalchemy.orm import relationship
from app.models.base import Base

class Cita(Base):
    __tablename__ = 'citas'
    
    id_cita = Column(Integer, primary_key=True)
    fec_en = Column(Date, nullable=False)
    hora_cita_inicio = Column(TIMESTAMP, nullable=False)
    hora_cita_termino = Column(TIMESTAMP, nullable=False)
    motivo_cita = Column(String(500), nullable=False)
    token_cita = Column(String(100), nullable=False, unique=True)
    id_medico = Column(Integer, ForeignKey('medicos.id_medico'), nullable=False)
    id_paciente = Column(Integer, ForeignKey('pacientes.id_paciente'), nullable=False)
    id_seguro = Column(Integer, ForeignKey('seguros.id_seguro'), nullable=False)
    id_estado = Column(Integer, ForeignKey('estados.id_estado'), nullable=False)
    
    # Relaciones
    medico = relationship('Medico', backref='citas')
    paciente = relationship('Paciente', backref='citas')
    seguro = relationship('Seguro', backref='citas')
    estado = relationship('Estado', backref='citas') 
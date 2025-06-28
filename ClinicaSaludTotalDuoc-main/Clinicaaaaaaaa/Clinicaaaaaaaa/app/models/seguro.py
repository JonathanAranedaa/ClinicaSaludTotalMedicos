from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.models.base import Base

class Seguro(Base):
    __tablename__ = 'seguros'
    
    id_seguro = Column(Integer, primary_key=True)
    nom_seguro = Column(String(200), nullable=False)
    numero_poliza = Column(String(200), nullable=False)
    fec_inicio = Column(Date, nullable=False)
    fec_termino = Column(Date, nullable=False)
    fec_registro = Column(Date, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    id_estado = Column(Integer, ForeignKey('estados.id_estado'), nullable=False)
    
    # Relaciones
    estado = relationship('Estado', backref='seguros') 
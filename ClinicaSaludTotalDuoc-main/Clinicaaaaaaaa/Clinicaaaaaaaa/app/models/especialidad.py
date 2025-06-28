from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base

class Especialidades(Base):
    __tablename__ = 'especialidades'
    
    id_especialidad = Column(Integer, primary_key=True)
    nom_espe = Column(String(200), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<Especialidades {self.nom_espe}>"

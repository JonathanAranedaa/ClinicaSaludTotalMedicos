from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Estado(Base):
    __tablename__ = 'estados'
    
    id_estado = Column(Integer, primary_key=True)
    estado = Column(String(200), nullable=False) 
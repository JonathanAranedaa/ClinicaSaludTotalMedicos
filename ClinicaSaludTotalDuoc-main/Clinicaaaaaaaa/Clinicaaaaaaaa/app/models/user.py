from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey, Date, Sequence
from sqlalchemy.orm import relationship
from app.models.base import Base
from werkzeug.security import generate_password_hash, check_password_hash

# Tabla de relación usuarios_roles
usuarios_roles = Table('usuarios_roles',
    Base.metadata,
    Column('id_usuario', Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True),
    Column('id_rol', Integer, ForeignKey('roles.id_rol', ondelete='CASCADE'), primary_key=True)
)

class User(UserMixin, Base):
    __tablename__ = 'usuarios'
    
    id_usuario = Column(Integer, Base.generate_id('usuarios'), primary_key=True)
    rut = Column(String(12), nullable=False)
    correo = Column(String(200), nullable=False)
    contrasena = Column(String(200), nullable=False)
    nombre = Column(String(200), nullable=False)
    ap_paterno = Column(String(200), nullable=False)
    ap_materno = Column(String(200), nullable=False)
    sexo = Column(Boolean, nullable=False)
    direccion = Column(String(200), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    
    # Relaciones
    roles = relationship('Role', secondary=usuarios_roles, backref='usuarios')
    
    def check_password(self, password):
        if self.contrasena is None or password is None:
            return False
        return str(self.contrasena).strip() == str(password).strip()
    
    def __repr__(self):
        return f"<User {self.nombre} {self.ap_paterno}>"
    
    def get_id(self):
        return str(self.id_usuario)

class Role(Base):
    __tablename__ = 'roles'
    
    id_rol = Column(Integer, primary_key=True)
    nombre_rol = Column(String(100), nullable=False, unique=True)

class Paciente(Base):
    __tablename__ = 'pacientes'
    
    id_paciente = Column(Integer, Sequence('pacientes_id_paciente_seq'), primary_key=True)
    fecha_nac = Column(Date, nullable=False)
    telefono = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    fec_reg = Column(Date, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    
    # Relaciones
    usuario = relationship('User', backref='paciente')

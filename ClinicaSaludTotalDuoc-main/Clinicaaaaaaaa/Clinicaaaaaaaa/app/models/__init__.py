from .base import Base
from .user import User, Role, Paciente
from .especialidad import Especialidades
from .medico import Medico
from .horario import Horario
from .cita import Cita
from .estado import Estado
from .seguro import Seguro

__all__ = [
    'Base',
    'User',
    'Role',
    'Paciente',
    'Especialidades',
    'Medico',
    'Horario',
    'Cita',
    'Estado',
    'Seguro'
]

# Inicializar las tablas
from .especialidad import Especialidades
from .user import User
from .medico import Medico
from .horario import Horario

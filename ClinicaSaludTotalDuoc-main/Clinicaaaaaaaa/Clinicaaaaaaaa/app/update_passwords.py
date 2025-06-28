from models.user import User
from models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

# Configuración de la base de datos
engine = create_engine('postgresql://Administrador:Integracion2025%25@clinicadb.postgres.database.azure.com:5432/clinicaDB')
Session = sessionmaker(bind=engine)

# Actualizar contraseñas
session = Session()
try:
    # Obtener todos los usuarios
    users = session.query(User).all()
    
    for user in users:
        # Generar hash de la contraseña
        hashed_password = generate_password_hash(user.contrasena)
        # Actualizar la contraseña
        user.contrasena = hashed_password
        print(f"Actualizando contraseña para {user.nombre} {user.appaterno}")
    
    # Guardar cambios
    session.commit()
    print("Contraseñas actualizadas exitosamente")
except Exception as e:
    print(f"Error: {str(e)}")
    session.rollback()
finally:
    session.close()

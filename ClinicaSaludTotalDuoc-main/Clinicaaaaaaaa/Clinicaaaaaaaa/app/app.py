from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, login_user, logout_user, current_user
from flask_cors import CORS
from sqlalchemy import select, create_engine, text
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from config import Config
from app.extensions import db, login_manager, cors
from app.models.base import Base
from app.models.user import User, Role
from app.models.medico import Medico
from app.models.especialidad import Especialidades
from app.models.horario import Horario
from app.models.retroalimentacion import Retroalimentacion
from app.forms import LoginForm, MedicoForm, EliminarMedicoForm, EditarMedicoForm
from app.errors import LoginError
import datetime

def create_app():
    app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    
    # Configurar logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # Deshabilitar CSRF para los tests
    app.config['WTF_CSRF_ENABLED'] = False if app.testing else True
    
    # Configurar la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Administrador:Integracion2025%25@clinicadb.postgres.database.azure.com:5432/clinicaDB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_timeout': 10,
        'pool_pre_ping': True,
        'max_overflow': 10
    }
    
    # Inicializar extensiones
    db.init_app(app)
    cors.init_app(app)
    
    # Inicializar login manager
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Registrar los modelos
    with app.app_context():
        Base.metadata.create_all(bind=db.engine)
        
        # Crear las secuencias si no existen
        try:
            db.session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'usuarios_id_seq') THEN
                        CREATE SEQUENCE usuarios_id_seq;
                    END IF;
                END $$;
                
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'pacientes_id_seq') THEN
                        CREATE SEQUENCE pacientes_id_seq;
                    END IF;
                END $$;
                
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'medicos_id_seq') THEN
                        CREATE SEQUENCE medicos_id_seq;
                    END IF;
                END $$;
                
                -- Restablecer las secuencias
                SELECT setval('usuarios_id_seq', COALESCE((SELECT MAX(id_usuario) FROM usuarios), 0) + 1, false);
                SELECT setval('pacientes_id_seq', COALESCE((SELECT MAX(id_paciente) FROM pacientes), 0) + 1, false);
                SELECT setval('medicos_id_seq', COALESCE((SELECT MAX(id_medico) FROM medicos), 0) + 1, false);
            """))
            db.session.commit()
            print("Secuencias creadas y restablecidas correctamente")
        except Exception as e:
            print(f"Error al restablecer secuencias: {str(e)}")
            db.session.rollback()
    
    # Configurar el manejador de usuarios
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    return app

app = create_app()

# Configurar CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/medico/<int:id_medico>/horarios', methods=['GET'])
def get_horarios_medico(id_medico):
    try:
        print(f"Solicitud de horarios para médico ID: {id_medico}")
        
        # Consulta para obtener los horarios del médico
        horarios = db.session.query(Horario).filter(
            Horario.id_medico == id_medico,
            Horario.activo == True
        ).order_by(
            Horario.dia_semana,
            Horario.hora_inicio
        ).all()
        
        print(f"Horarios encontrados: {len(horarios)}")
        print("Datos brutos de la consulta:")
        for horario in horarios:
            print(f"- Día: {horario.dia_semana}, Hora inicio: {horario.hora_inicio}, Hora salida: {horario.hora_salida}")
        
        # Formatear los resultados
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        horarios_formateados = []
        
        for horario in horarios:
            # Si dia_semana es string tipo 'Lunes', 'Martes', etc.
            dia_nombre = horario.dia_semana if horario.dia_semana in dias_semana else str(horario.dia_semana)
            horario_data = {
                'diaSemana': dia_nombre,
                'horaInicio': horario.hora_inicio.strftime('%H:%M'),
                'horaSalida': horario.hora_salida.strftime('%H:%M'),
                'idHorario': str(horario.id_horario) if hasattr(horario, 'id_horario') else str(horario.id),
                'fecha': dia_nombre  # Si tienes una fecha real, cámbiala aquí
            }
            horarios_formateados.append(horario_data)
            print(f"Horario formateado: {horario_data}")
        
        print("\nHorarios formateados completos:")
        for horario in horarios_formateados:
            print(f"- Día: {horario['diaSemana']}, Hora inicio: {horario['horaInicio']}")
        
        return jsonify(horarios_formateados)
        
    except Exception as e:
        error_msg = f"Error al obtener horarios: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/get_doctors', methods=['GET'])
def get_doctors():
    try:
        # Consulta para obtener todos los médicos con sus usuarios relacionados
        medicos = db.session.query(Medico, User).join(User).all()
        
        # Formatear los resultados
        medicos_formateados = []
        for medico, usuario in medicos:
            try:
                medico_data = {
                    'id': str(medico.id_medico),
                    'nombre': f"{usuario.nombre} {usuario.ap_paterno} {usuario.ap_materno}"
                }
                medicos_formateados.append(medico_data)
            except Exception as e:
                print(f"Error al procesar médico {medico.id_medico}: {str(e)}")
                continue
        
        return jsonify(medicos_formateados)
        
    except Exception as e:
        error_msg = f"Error al obtener médicos: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/get_doctor_schedule', methods=['POST'])
def get_doctor_schedule():
    try:
        doctor_id = request.args.get('doctor_id')
        if not doctor_id:
            return jsonify({'error': 'Doctor ID is required'}), 400
            
        # Consulta para obtener los horarios del médico
        horarios = db.session.query(Horario).filter(
            Horario.id_medico == doctor_id,
            Horario.activo == True
        ).all()
        
        # Formatear los resultados
        horarios_formateados = []
        for horario in horarios:
            horario_data = {
                'diaSemana': horario.dia_semana.strftime('%Y-%m-%d'),
                'horaInicio': horario.hora_inicio.strftime('%H:%M'),
                'horaSalida': horario.hora_salida.strftime('%H:%M')
            }
            horarios_formateados.append(horario_data)
        
        return jsonify(horarios_formateados)
        
    except Exception as e:
        error_msg = f"Error al obtener horarios: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/especialidades', methods=['POST'])
def create_especialidad():
    try:
        data = request.get_json()
        
        # Validar que el nombre esté presente
        if 'nom_espe' not in data:
            return jsonify({'error': 'Falta el nombre de la especialidad'}), 400
            
        nueva_especialidad = Especialidades(
            nom_espe=data['nom_espe']
        )
        db.session.add(nueva_especialidad)
        db.session.commit()
        
        # Asegurarse de que el id se haya generado correctamente
        db.session.refresh(nueva_especialidad)
        
        return jsonify({
            'id_especialidad': nueva_especialidad.id_especialidad,
            'nom_espe': nueva_especialidad.nom_espe
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    try:
        data = request.get_json()
        print(f"Datos recibidos en POST usuarios: {data}")
        
        # Validar que todos los campos requeridos estén presentes
        required_fields = ['rut', 'correo', 'contrasena', 'nombre', 'ap_paterno', 'ap_materno', 'sexo', 'direccion', 'activo']
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({'error': f'Faltan campos requeridos: {missing_fields}'}), 400
            
        # Hashear la contraseña
        hashed_password = generate_password_hash(data['contrasena'])
            
        nuevo_usuario = User(
            rut=data['rut'],
            correo=data['correo'],
            contrasena=hashed_password,
            nombre=data['nombre'],
            ap_paterno=data['ap_paterno'],
            ap_materno=data['ap_materno'],
            sexo=data['sexo'],
            direccion=data['direccion'],
            activo=data['activo']
        )
        print(f"Usuario creado: {nuevo_usuario}")
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        # Asegurarse de que el id se haya generado correctamente
        db.session.refresh(nuevo_usuario)
        print(f"ID usuario generado: {nuevo_usuario.id_usuario}")
        
        return jsonify({
            'id_usuario': nuevo_usuario.id_usuario,
            'rut': nuevo_usuario.rut,
            'correo': nuevo_usuario.correo,
            'nombre': nuevo_usuario.nombre,
            'ap_paterno': nuevo_usuario.ap_paterno,
            'ap_materno': nuevo_usuario.ap_materno,
            'sexo': nuevo_usuario.sexo,
            'direccion': nuevo_usuario.direccion,
            'activo': nuevo_usuario.activo
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error en POST usuarios: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/medicos', methods=['POST'])
def create_medico():
    try:
        data = request.get_json()
        print(f"Datos recibidos en POST medicos: {data}")
        
        # Validar que todos los campos requeridos estén presentes
        required_fields = ['certificacion', 'activo', 'id_especialidad', 'id_usuario']
        print(f"Campos requeridos: {required_fields}")
        print(f"Campos presentes: {[field for field in data.keys() if field in required_fields]}")
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({'error': f'Faltan campos requeridos: {missing_fields}'}), 400
            
        # Verificar que el usuario exista
        print(f"Buscando usuario con ID: {data['id_usuario']}")
        usuario = db.session.get(User, data['id_usuario'])
        if not usuario:
            print(f"Usuario no encontrado: {data['id_usuario']}")
            return jsonify({'error': 'Usuario no encontrado'}), 400
            
        # Verificar que la especialidad exista
        print(f"Buscando especialidad con ID: {data['id_especialidad']}")
        especialidad = db.session.get(Especialidades, data['id_especialidad'])
        if not especialidad:
            print(f"Especialidad no encontrada: {data['id_especialidad']}")
            return jsonify({'error': 'Especialidad no encontrada'}), 400
            
        nuevo_medico = Medico(
            certificacion=data['certificacion'],
            activo=data['activo'],
            id_especialidad=data['id_especialidad'],
            id_usuario=data['id_usuario']
        )
        print(f"Medico creado: {nuevo_medico}")
        db.session.add(nuevo_medico)
        db.session.commit()
        
        # Asegurarse de que el id se haya generado correctamente
        db.session.refresh(nuevo_medico)
        print(f"ID médico generado: {nuevo_medico.id_medico}")
        
        return jsonify({
            'id_medico': nuevo_medico.id_medico,
            'certificacion': nuevo_medico.certificacion,
            'activo': nuevo_medico.activo,
            'id_especialidad': nuevo_medico.id_especialidad,
            'id_usuario': nuevo_medico.id_usuario
        }), 201
        print(f"Datos recibidos en POST medicos: {data}")
        
        # Validar que todos los campos requeridos estén presentes
        required_fields = ['certificacion', 'activo', 'id_especialidad', 'id_usuario']
        print(f"Campos requeridos: {required_fields}")
        print(f"Campos presentes: {[field for field in data.keys() if field in required_fields]}")
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({'error': f'Faltan campos requeridos: {missing_fields}'}), 400
            
        # Verificar que el usuario exista
        print(f"Buscando usuario con ID: {data['id_usuario']}")
        usuario = db.session.get(User, data['id_usuario'])
        if not usuario:
            print(f"Usuario no encontrado: {data['id_usuario']}")
            return jsonify({'error': 'Usuario no encontrado'}), 400
            
        # Verificar que la especialidad exista
        print(f"Buscando especialidad con ID: {data['id_especialidad']}")
        especialidad = db.session.get(Especialidades, data['id_especialidad'])
        if not especialidad:
            print(f"Especialidad no encontrada: {data['id_especialidad']}")
            return jsonify({'error': 'Especialidad no encontrada'}), 400
            
        nuevo_medico = Medico(
            certificacion=data['certificacion'],
            activo=data['activo'],
            id_especialidad=data['id_especialidad'],
            id_usuario=data['id_usuario']
        )
        print(f"Medico creado: {nuevo_medico}")
        db.session.add(nuevo_medico)
        db.session.commit()
        
        # Asegurarse de que el id se haya generado correctamente
        db.session.refresh(nuevo_medico)
        print(f"ID médico generado: {nuevo_medico.id_medico}")
        
        return jsonify({
            'id_medico': nuevo_medico.id_medico,
            'certificacion': nuevo_medico.certificacion,
            'activo': nuevo_medico.activo,
            'id_especialidad': nuevo_medico.id_especialidad,
            'id_usuario': nuevo_medico.id_usuario
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error en POST medicos: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/medicos/<int:id_medico>', methods=['GET', 'POST'])
def medico_route(id_medico):
    try:
        if request.method == 'GET':
            medico = db.session.get(Medico, id_medico)
            if not medico:
                return jsonify({'error': 'Médico no encontrado'}), 404
            return jsonify({
                'id_medico': medico.id_medico,
                'certificacion': medico.certificacion,
                'activo': medico.activo,
                'id_especialidad': medico.id_especialidad,
                'id_usuario': medico.id_usuario
            }), 200
        
        # Para POST (actualizar)
        medico = db.session.get(Medico, id_medico)
        if not medico:
            return jsonify({'error': 'Médico no encontrado'}), 404
            
        data = request.get_json()
        
        # Validar que los campos a actualizar sean válidos
        allowed_fields = ['certificacion', 'activo', 'id_especialidad']
        invalid_fields = [field for field in data.keys() if field not in allowed_fields]
        if invalid_fields:
            return jsonify({'error': f'Campos no válidos: {invalid_fields}'}), 400
            
        for key, value in data.items():
            setattr(medico, key, value)
        
        db.session.commit()
        return jsonify({
            'id_medico': medico.id_medico,
            'certificacion': medico.certificacion,
            'activo': medico.activo,
            'id_especialidad': medico.id_especialidad,
            'id_usuario': medico.id_usuario
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        correo = form.username.data
        contrasena = form.password.data
        try:
            print(f"Buscando usuario con correo: {correo}")
            user = db.session.execute(
                select(User).where(User.correo == correo)
            ).scalar_one_or_none()
            if user:
                print(f"Usuario encontrado: {user.correo} (ID: {user.id_usuario})")
                print(f"Detalles del usuario: {user.__dict__}")
                if user.check_password(contrasena):
                    print("Contraseña válida")
                    try:
                        # Verificar si el usuario tiene el rol de administrador
                        admin_role = db.session.execute(
                            select(Role).where(Role.nombre_rol == 'Administrador')
                        ).scalar_one_or_none()
                        
                        if admin_role and admin_role in user.roles:
                            print("Usuario es administrador")
                            # Limpiar la sesión anterior
                            session.clear()
                            # Establecer datos de sesión del administrador
                            session['tipo_usuario'] = 'Administrador'
                            session['user_id'] = user.id_usuario
                            print(f"Sesión establecida: {dict(session)}")
                            
                            login_user(user)
                            db.session.commit()
                            flash('Inicio de sesión exitoso como administrador.', 'success')
                            return redirect(url_for('dashboard'))
                        else:
                            print("No es administrador")
                            raise LoginError.not_admin()
                    except Exception as e:
                        print(f"Error en la verificación de rol: {str(e)}")
                        raise LoginError.not_admin()
                else:
                    print("Contraseña inválida")
                    raise LoginError.invalid_credentials()
            else:
                print("Usuario no encontrado")
                raise LoginError.user_not_found()
        except LoginError as e:
            flash(str(e))
            return render_template('login.html', form=form)
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            flash('Error inesperado al iniciar sesión.')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/medicos')
@login_required
def medicos():
    try:
        print("Cargando lista de médicos...")
        # Contar médicos
        total_medicos = db.session.query(Medico).count()
        print(f"Total de médicos: {total_medicos}")
        
        # Obtener todos los médicos con sus datos relacionados y sexo
        medicos = db.session.query(
            Medico.id_medico,
            User.nombre,
            User.ap_paterno,
            User.ap_materno,
            User.sexo,
            Especialidades.nom_espe,
            Medico.certificacion,
            Medico.activo
        ).join(User, Medico.id_usuario == User.id_usuario)\
          .join(Especialidades, Medico.id_especialidad == Especialidades.id_especialidad)\
          .order_by(User.ap_paterno, User.ap_materno, User.nombre).all()
        
        print(f"Médicos encontrados: {len(medicos)}")
        
        # Preparar los datos para el template
        medicos_list = []
        for medico in medicos:
            titulo = "Dr." if medico.sexo else "Dra."
            nombre_completo = f"{titulo} {medico.nombre} {medico.ap_paterno} {medico.ap_materno}"
            medico_data = {
                'id': medico.id_medico,
                'nombre': nombre_completo,
                'especialidad': medico.nom_espe,
                'estado': 'Activo' if medico.activo else 'Inactivo',
                'activo': medico.activo,
                'certificacion': medico.certificacion,
                'nombre_raw': medico.nombre,
                'ap_paterno': medico.ap_paterno,
                'ap_materno': medico.ap_materno
            }
            medicos_list.append(medico_data)
            print(f"Procesado médico: {nombre_completo}")
        
        # Crear el formulario de eliminación
        form_eliminar = EliminarMedicoForm()
        
        return render_template('medicos.html', 
                            total_medicos=total_medicos,
                            medicos=medicos_list,
                            form_eliminar=form_eliminar)
    except Exception as e:
        print(f'Error al cargar los médicos: {str(e)}')
        flash(f'Error al cargar los médicos: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/agregarmedico', methods=['GET', 'POST'], endpoint='agregar_medico')
@login_required
def agregar_medico():
    form = MedicoForm()
    try:
        especialidades = db.session.query(Especialidades).all()
        form.idespecialidad.choices = [(especialidad.id_especialidad, especialidad.nom_espe) for especialidad in especialidades]
        
        if form.validate_on_submit():
            # Primero obtener la especialidad
            especialidad = db.session.query(Especialidades).filter_by(id_especialidad=form.idespecialidad.data).first()
            
            if not especialidad:
                flash('Especialidad no encontrada', 'error')
                return redirect(url_for('agregar_medico'))
            
            # Crear nuevo usuario usando los valores generados del formulario
            nuevo_usuario = User(
                rut=form.rut.data,
                correo=form.correo.data,
                contrasena=form.contrasena.data,
                nombre=form.nombre.data,
                ap_paterno=form.apPaterno.data,
                ap_materno=form.apMaterno.data,
                sexo=form.sexo.data,
                direccion=form.direccion.data,
                activo=True
            )
            
            try:
                print("\n=== INICIANDO PROCESO DE CREACIÓN DE MÉDICO ===")
                print("Datos del formulario:")
                print(f"RUT: {form.rut.data}")
                print(f"Correo: {form.correo.data}")
                print(f"Nombre: {form.nombre.data}")
                print(f"Apellido Paterno: {form.apPaterno.data}")
                print(f"Apellido Materno: {form.apMaterno.data}")
                print(f"Sexo: {form.sexo.data}")
                print(f"Dirección: {form.direccion.data}")
                print(f"Certificación: {form.certificacion.data}")
                print(f"ID Especialidad: {form.idespecialidad.data}")
                
                print("\n=== CREANDO USUARIO ===")
                print("Datos del nuevo usuario:", nuevo_usuario.__dict__)
                
                # Primero guardar el usuario para obtener su ID
                try:
                    db.session.add(nuevo_usuario)
                    print("Usuario agregado a la sesión")
                    db.session.flush()
                    print(f"Flush realizado. ID de usuario generado: {nuevo_usuario.id_usuario}")
                    # Insertar en usuarios_roles (id_rol=2 para médico)
                    db.session.execute(
                        text("INSERT INTO usuarios_roles (id_usuario, id_rol) VALUES (:id_usuario, :id_rol)"),
                        {"id_usuario": nuevo_usuario.id_usuario, "id_rol": 2}
                    )
                    print("Registro en usuarios_roles insertado")
                except Exception as e:
                    print(f"Error al crear usuario: {str(e)}")
                    raise
                
                print("\n=== CREANDO MÉDICO ===")
                # Ahora crear el médico con el ID del usuario
                nuevo_medico = Medico(
                    certificacion=form.certificacion.data,
                    activo=True,
                    id_especialidad=especialidad.id_especialidad,
                    id_usuario=nuevo_usuario.id_usuario
                )
                print("Datos del nuevo médico:", nuevo_medico.__dict__)
                
                try:
                    # Agregar el médico a la sesión
                    db.session.add(nuevo_medico)
                    print("Médico agregado a la sesión")
                    
                    # Guardar todos los cambios
                    db.session.commit()
                    print("Commit realizado exitosamente")
                    
                    # Verificar que se guardó correctamente
                    usuario_guardado = db.session.query(User).filter_by(id_usuario=nuevo_usuario.id_usuario).first()
                    medico_guardado = db.session.query(Medico).filter_by(id_usuario=nuevo_usuario.id_usuario).first()
                    
                    print("\n=== VERIFICACIÓN DE GUARDADO ===")
                    print(f"Usuario guardado: {usuario_guardado is not None}")
                    if usuario_guardado:
                        print(f"Datos del usuario guardado: {usuario_guardado.__dict__}")
                    print(f"Médico guardado: {medico_guardado is not None}")
                    if medico_guardado:
                        print(f"Datos del médico guardado: {medico_guardado.__dict__}")
                    
                    flash('Médico agregado exitosamente.', 'success')
                    return redirect(url_for('medicos'))
                except Exception as e:
                    print(f"Error al guardar médico: {str(e)}")
                    raise
                    
            except Exception as e:
                print(f"\n=== ERROR EN EL PROCESO ===")
                print(f"Error completo: {str(e)}")
                print(f"Tipo de error: {type(e)}")
                db.session.rollback()
                flash(f'Error al agregar el médico: {str(e)}', 'error')
                return render_template('agregarmedico.html', form=form, especialidades=especialidades)
            finally:
                print("\n=== FIN DEL PROCESO ===\n")
        
        return render_template('agregarmedico.html', form=form, especialidades=especialidades)
    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'error')
        return redirect(url_for('agregar_medico'))

@app.route('/detalle_medico/<int:idmedico>')
@login_required
def detalle_medico(idmedico):
    try:
        # Obtener el médico con sus datos relacionados
        medico = db.session.query(Medico).join(User, Medico.id_usuario == User.id_usuario).join(Especialidades, Medico.id_especialidad == Especialidades.id_especialidad).filter(Medico.id_medico == idmedico).first()
        
        if not medico:
            flash('Médico no encontrado', 'error')
            return redirect(url_for('medicos'))
        
        # Preparar los datos para el template
        medico_data = {
            'id': medico.id_medico,
            'rut': medico.usuario.rut,
            'nombre': medico.usuario.nombre,
            'ap_paterno': medico.usuario.ap_paterno,
            'ap_materno': medico.usuario.ap_materno,
            'nombre_completo': f"{medico.usuario.nombre} {medico.usuario.ap_paterno} {medico.usuario.ap_materno}",
            'especialidad': medico.especialidad.nom_espe,
            'certificacion': medico.certificacion,
            'estado': 'Activo' if medico.activo else 'Inactivo',
            'correo': medico.usuario.correo,
            'direccion': medico.usuario.direccion,
            'sexo': 'Masculino' if medico.usuario.sexo else 'Femenino'
        }
        
        return render_template('detalle_medico.html', medico=medico_data)
    except Exception as e:
        print(f"Error al cargar detalle del médico: {str(e)}")
        flash(f'Error al cargar el detalle del médico: {str(e)}', 'error')
        return redirect(url_for('medicos'))

@app.route('/editar_medico/<int:idmedico>', methods=['GET', 'POST'])
@login_required
def editar_medico(idmedico):
    try:
        # Obtener el médico y su usuario
        medico = db.session.query(Medico).join(User, Medico.id_usuario == User.id_usuario).filter(Medico.id_medico == idmedico).first()
        
        if not medico:
            flash('Médico no encontrado', 'error')
            return redirect(url_for('medicos'))
        
        # Crear el formulario y poblarlo con los datos existentes
        form = EditarMedicoForm(obj=medico.usuario)
        form.certificacion.data = medico.certificacion
        form.activo.data = medico.activo
        
        if form.validate_on_submit():
            try:
                print("Actualizando datos del médico...")
                # Actualizar el usuario
                medico.usuario.nombre = form.nombre.data
                medico.usuario.ap_paterno = form.apPaterno.data
                medico.usuario.ap_materno = form.apMaterno.data
                medico.usuario.direccion = form.direccion.data
                
                # Actualizar el médico
                medico.certificacion = form.certificacion.data
                medico.activo = form.activo.data
                
                # Guardar los cambios
                db.session.commit()
                print("Médico actualizado exitosamente")
                flash('Médico actualizado exitosamente', 'success')
                return redirect(url_for('medicos'))
            except Exception as e:
                print(f"Error al actualizar médico: {str(e)}")
                db.session.rollback()
                flash(f'Error al actualizar el médico: {str(e)}', 'error')
        
        return render_template('editarmedico.html', form=form, medico=medico)
    except Exception as e:
        print(f"Error al cargar formulario de edición: {str(e)}")
        flash(f'Error al editar el médico: {str(e)}', 'error')
        return redirect(url_for('medicos'))

@app.route('/horarios', methods=['GET', 'POST'])
@login_required
def horarios():
    medicos_list = []  # Inicializar antes del try
    try:
        # Obtener todos los médicos con sus datos relacionados
        medicos = db.session.query(
            Medico.id_medico,
            User.nombre,
            User.ap_paterno,
            User.ap_materno,
            User.sexo
        ).join(User, Medico.id_usuario == User.id_usuario).all()
        
        # Preparar los datos para el template
        medicos_list = []
        for medico in medicos:
            titulo = "Dr." if medico.sexo else "Dra."
            nombre_completo = f"{titulo} {medico.nombre} {medico.ap_paterno} {medico.ap_materno}"
            medico_data = {
                'id': medico.id_medico,
                'nombre': nombre_completo
            }
            medicos_list.append(medico_data)
        
        if request.method == 'POST':
            csrf_token = request.headers.get('X-CSRFToken')
            if not csrf_token:
                return jsonify({'error': 'Token CSRF requerido'}), 400
            try:
                data = request.get_json()
                print(f"Datos recibidos: {data}")
                if not data:
                    return jsonify({'error': 'No se recibieron datos'}), 400
                id_medico = data.get('id_medico') or data.get('idmedico')
                if id_medico is None:
                    return jsonify({'error': 'Falta el id del médico'}), 400
                id_medico = int(id_medico)
                activo = data.get('activo', True)
                horarios = data.get('horarios', [])
                print(f"ID médico: {id_medico}")
                print(f"Activo: {activo}")
                print(f"Horarios: {horarios}")
                if not id_medico or not horarios:
                    return jsonify({'error': 'Faltan datos requeridos'}), 400
                db.session.query(Horario).filter_by(id_medico=id_medico).delete()
                nuevos_horarios = []
                for horario in horarios:
                    try:
                        print(f"Procesando horario: {horario}")
                        fecha = datetime.datetime.strptime(horario['date'], '%d/%m/%Y').date()
                        fecha_str = fecha.strftime('%Y-%m-%d')
                        inicio = datetime.datetime.strptime(horario['inicio'], '%H:%M').time()
                        fin = datetime.datetime.strptime(horario['fin'], '%H:%M').time()
                        print(f"Fecha: {fecha_str}")
                        print(f"Hora inicio: {inicio}")
                        print(f"Hora fin: {fin}")
                        if fin <= inicio:
                            return jsonify({
                                'error': f'La hora fin debe ser mayor que la hora inicio para {horario["date"]}'
                            }), 400
                        if fecha < datetime.datetime.now().date():
                            return jsonify({
                                'error': f'La fecha {fecha} no puede ser en el pasado'
                            }), 400
                        if fin <= inicio:
                            return jsonify({
                                'error': f'La hora fin debe ser mayor que la hora inicio para {fecha}'
                            }), 400
                        nuevo_horario = Horario(
                            id_medico=id_medico,
                            dia_semana=fecha_str,
                            hora_inicio=inicio,
                            hora_salida=fin,
                            activo=activo
                        )
                        nuevos_horarios.append(nuevo_horario)
                    except ValueError as ve:
                        print(f"Error de formato en horario {horario['date']}: {str(ve)}")
                        return jsonify({
                            'error': f'Error en el formato de los datos para {horario["date"]}: {str(ve)}'
                        }), 400
                    except Exception as e:
                        print(f"Error procesando horario {horario['date']}: {str(e)}")
                        return jsonify({
                            'error': f'Error procesando horario para {horario["date"]}: {str(e)}'
                        }), 400
                db.session.add_all(nuevos_horarios)
                db.session.commit()
                return jsonify({
                    'message': 'Horarios guardados exitosamente',
                    'total': len(nuevos_horarios)
                }), 200
            except Exception as e:
                db.session.rollback()
                print(f"Error general al guardar los horarios: {str(e)}")
                return jsonify({'error': f'Error al guardar los horarios: {str(e)}'}), 500
        return render_template('horarioslaborales.html', medicos=medicos_list)
    except Exception as e:
        flash(f'Error al cargar los médicos: {str(e)}', 'error')
        return render_template('horarioslaborales.html', medicos=medicos_list)

@app.route('/cambiar_estado_medico/<int:idmedico>', methods=['POST'])
@login_required
def cambiar_estado_medico(idmedico):
    try:
        print(f"Cambiando estado del médico {idmedico}")
        # Obtener el médico
        medico = db.session.query(Medico).filter(Medico.id_medico == idmedico).first()
        
        if not medico:
            print(f"Médico {idmedico} no encontrado")
            flash('Médico no encontrado', 'error')
            return redirect(url_for('medicos'))
        
        # Cambiar el estado del médico
        medico.activo = not medico.activo
        
        # Guardar los cambios
        db.session.commit()
        print(f"Estado del médico {idmedico} cambiado a {'activo' if medico.activo else 'inactivo'}")
        
        # Mostrar mensaje según el nuevo estado
        if medico.activo:
            flash('Médico habilitado exitosamente', 'success')
        else:
            flash('Médico deshabilitado exitosamente', 'success')
            
        return redirect(url_for('medicos'))
    except Exception as e:
        print(f"Error al cambiar estado del médico {idmedico}: {str(e)}")
        db.session.rollback()
        flash('Error al cambiar el estado del médico: ' + str(e), 'error')
        return redirect(url_for('medicos'))

@app.route('/eliminar_medico/<int:idmedico>', methods=['POST'])
@login_required
def eliminar_medico(idmedico):
    # Esta función ahora está deshabilitada y solo se mantiene por compatibilidad
    flash('Error: La eliminación de médicos está deshabilitada. Use la opción de deshabilitar en su lugar.', 'error')
    return redirect(url_for('medicos'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Médicos activos - usando la tabla medicos según definitivo.txt
        total_medicos_activos = db.session.execute(text('SELECT COUNT(*) FROM medicos WHERE activo = true')).scalar()
        print(f"Total médicos activos encontrados: {total_medicos_activos}")
        
        # Pacientes activos - usando la tabla pacientes según definitivo.txt
        total_pacientes = db.session.execute(text('SELECT COUNT(*) FROM pacientes WHERE activo = true')).scalar()
        print(f"Total pacientes activos encontrados: {total_pacientes}")
        
        # Citas de hoy (SQL puro)
        total_citas_hoy = db.session.execute(text("SELECT COUNT(*) FROM citas WHERE DATE(hora_cita_inicio) = CURRENT_DATE")).scalar()
        print(f"Total citas hoy: {total_citas_hoy}")
    except Exception as e:
        print(f"Error al obtener estadísticas del dashboard: {str(e)}")
        total_medicos_activos = 0
        total_pacientes = 0
        total_citas_hoy = 0

    # Actividad reciente: últimos médicos, pacientes y citas
    actividades = []
    # Últimos médicos agregados o cambio de estado
    medicos_recientes = db.session.execute(text('SELECT m.id_medico, u.nombre, u.ap_paterno, m.activo, m.certificacion, m.id_usuario FROM medicos m JOIN usuarios u ON m.id_usuario = u.id_usuario ORDER BY m.id_medico DESC LIMIT 2')).fetchall()
    for m in medicos_recientes:
        estado = 'Completado' if m.activo else 'En curso'
        actividades.append({
            'descripcion': f"Médico {'habilitado' if m.activo else 'deshabilitado'}: Dr. {m.nombre} {m.ap_paterno}",
            'fecha': 'Reciente',
            'estado': estado
        })
    # Últimos pacientes registrados
    pacientes_recientes = db.session.execute(text('SELECT id_paciente, id_usuario FROM pacientes ORDER BY id_paciente DESC LIMIT 2')).fetchall()
    for p in pacientes_recientes:
        usuario = db.session.execute(
            text('SELECT nombre, ap_paterno FROM usuarios WHERE id_usuario=:id'),
            {'id': p.id_usuario}
        ).fetchone()
        if usuario:
            actividades.append({
                'descripcion': f"Nuevo paciente registrado: {usuario.nombre} {usuario.ap_paterno}",
                'fecha': 'Reciente',
                'estado': 'Completado'
            })
    # Últimas citas agendadas
    citas_recientes = db.session.execute(text('SELECT id_cita, hora_cita_inicio, id_paciente FROM citas ORDER BY hora_cita_inicio DESC LIMIT 2')).fetchall()
    for c in citas_recientes:
        paciente = db.session.execute(text('SELECT id_usuario FROM pacientes WHERE id_paciente=:id'), {'id': c.id_paciente}).fetchone()
        nombre = ''
        if paciente:
            usuario = db.session.execute(text('SELECT nombre, ap_paterno FROM usuarios WHERE id_usuario=:id'), {'id': paciente.id_usuario}).fetchone()
            if usuario:
                nombre = f"{usuario.nombre} {usuario.ap_paterno}"
        actividades.append({
            'descripcion': f"Nueva cita agendada para {nombre}",
            'fecha': str(c.hora_cita_inicio.date()),
            'estado': 'Pendiente'
        })
    # Ordenar por fecha (simulado, ya que usamos 'Reciente' y fechas)
    actividades = actividades[:5]
    return render_template('dashboard.html', user=current_user, total_medicos=total_medicos_activos, total_pacientes=total_pacientes, total_citas=total_citas_hoy, actividades=actividades)

@app.route('/retroalimentacionadmin')
@login_required
def retroalimentacionadmin():
    try:
        # Verificar que el usuario sea administrador
        if 'tipo_usuario' not in session or session['tipo_usuario'] != 'Administrador':
            flash('Acceso no autorizado. Debe ser administrador.', 'error')
            return redirect(url_for('dashboard'))

        # Obtener todas las retroalimentaciones y armar el nombre del médico
        retroalimentaciones = db.session.query(Retroalimentacion).order_by(Retroalimentacion.fecha.desc()).all()
        retro_list = []
        for retro in retroalimentaciones:
            medico = db.session.query(Medico).filter_by(id_medico=retro.id_medico).first()
            if medico and medico.usuario:
                nombre_medico = f"{medico.usuario.nombre} {medico.usuario.ap_paterno} {medico.usuario.ap_materno}"
            else:
                nombre_medico = "-"
            retro_list.append({
                'id': retro.id_retroalimentacion,
                'fecha': retro.fecha,
                'medico_nombre': nombre_medico,
                'tipo': retro.tipo,
                'mensaje': retro.mensaje,
                'estado': retro.estado
            })
        return render_template('retroalimentacionadmin.html', retroalimentaciones=retro_list)
    except Exception as e:
        flash(f'Error al cargar las retroalimentaciones: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/cambiar_estado_retroalimentacion/<int:idretro>', methods=['POST'])
@login_required
def cambiar_estado_retroalimentacion(idretro):
    try:
        retroalimentacion = db.session.query(Retroalimentacion).filter_by(id_retroalimentacion=idretro).first()
        if not retroalimentacion:
            flash('Retroalimentación no encontrada', 'error')
            return redirect(url_for('retroalimentacionadmin'))
        retroalimentacion.estado = 'Resuelta'
        db.session.commit()
        flash('Retroalimentación marcada como resuelta exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado de la retroalimentación: {str(e)}', 'error')
    return redirect(url_for('retroalimentacionadmin'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/horarios/save', methods=['POST'])
def save_horarios():
    try:
        print("\n=== STARTING SCHEDULE SAVE ===")
        print(f"Request headers: {dict(request.headers)}")  # Log all headers
        print(f"Request data (raw): {request.data}")
        print(f"Content type: {request.headers.get('Content-Type')}")
        
        # Get data
        try:
            data = request.get_json()
            if data is None:
                print("Error: No JSON data received")
                return jsonify({
                    'error': 'No se recibieron datos JSON',
                    'details': {
                        'headers': dict(request.headers),
                        'raw_data': request.data.decode('utf-8') if request.data else 'No data'
                    }
                }), 400
            
            print(f"=== RECEIVED DATA ===")
            print(f"Raw JSON data: {data}")
            print(f"idMedico type: {type(data.get('idMedico'))}")
            print(f"horarios type: {type(data.get('horarios'))}")
            print(f"horarios length: {len(data.get('horarios', []))}")
            print("=== END RECEIVED DATA ===")
            
            idMedico = data.get('id_medico') or data.get('idmedico')
            if idMedico is None:
                return jsonify({'error': 'Falta el id del médico'}), 400
            id_medico = int(idMedico)
            horarios = data.get('horarios')
            
            print(f"ID Medico: {id_medico}")
            print(f"Horarios: {horarios}")
            
            # Validate data
            if not id_medico or not horarios:
                print("Error: Faltan datos requeridos")
                return jsonify({
                    'error': 'Faltan datos requeridos',
                    'details': {'received_data': data}
                }), 400
                
            try:
                # Delete existing schedules for this doctor
                print(f"Deleting existing schedules for doctor {id_medico}")
                try:
                    # First check if the doctor exists
                    if not Medico.query.filter_by(id=id_medico).first():
                        print(f"Doctor with ID {id_medico} not found")
                        return jsonify({
                            'error': 'Médico no encontrado',
                            'details': {'doctor_id': id_medico}
                        }), 404
                    
                    # Delete existing schedules
                    deleted_count = Horario.query.filter_by(id_medico=id_medico).delete()
                    db.session.commit()
                    print(f"Deleted {deleted_count} existing schedules")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error deleting existing schedules: {str(e)}")
                    return jsonify({
                        'error': 'Error al eliminar horarios existentes',
                        'details': str(e)
                    }), 500
                
                # Insert new schedules
                print(f"Inserting {len(horarios)} new schedules")
                try:
                    for horario in horarios:
                        print(f"=== PROCESSING SCHEDULE ===")
                        print(f"Schedule data: {horario}")
                        print(f"Date: {horario.get('fecha')}")
                        print(f"Start time: {horario.get('horaInicio')}")
                        print(f"End time: {horario.get('horaFin')}")
                        print("=== END SCHEDULE DATA ===")
                        
                        if not all(key in horario for key in ['fecha', 'horaInicio', 'horaFin']):
                            print("Error: Invalid schedule format")
                            return jsonify({
                                'error': 'Formato de horario incorrecto',
                                'details': {'schedule': horario}
                            }), 400
                            
                        # Validate date format
                        try:
                            # Split date components
                            day, month, year = map(int, horario['fecha'].split('/'))
                            
                            # Validate date components
                            if not (1 <= day <= 31 and 1 <= month <= 12):
                                raise ValueError('Fecha inválida: día o mes fuera de rango')
                            
                            # Create datetime object
                            date_obj = datetime(year, month, day)
                            print(f"Date parsed successfully: {date_obj}")
                            
                            # Validate date range
                            today = datetime.datetime.now()
                            if date_obj < today:
                                raise ValueError('La fecha no puede ser anterior a hoy')
                        except ValueError as e:
                            print(f"Error parsing date {horario['fecha']}: {str(e)}")
                            return jsonify({
                                'error': f'Formato de fecha incorrecto. Use DD/MM/YYYY: {str(e)}',
                                'details': {
                                    'date': horario['fecha'],
                                    'error': str(e)
                                }
                            }), 400
                            
                        # Validate time format
                        try:
                            datetime.datetime.strptime(horario['horaInicio'], '%H:%M')
                            datetime.datetime.strptime(horario['horaFin'], '%H:%M')
                        except ValueError:
                            return jsonify({
                                'error': 'Formato de hora incorrecto. Use HH:MM',
                                'details': {
                                    'horaInicio': horario['horaInicio'],
                                    'horaFin': horario['horaFin']
                                }
                            }), 400
                            
                        fecha = datetime.datetime.strptime(horario['date'], '%d/%m/%Y').date()
                        fecha_str = fecha.strftime('%Y-%m-%d')
                        inicio = datetime.datetime.strptime(horario['inicio'], '%H:%M').time()
                        fin = datetime.datetime.strptime(horario['fin'], '%H:%M').time()
                        print(f"Fecha: {fecha_str}")
                        print(f"Hora inicio: {inicio}")
                        print(f"Hora fin: {fin}")
                        if fin <= inicio:
                            return jsonify({
                                'error': f'La hora fin debe ser mayor que la hora inicio para {horario["date"]}'
                            }), 400
                        if fecha < datetime.datetime.now().date():
                            return jsonify({
                                'error': f'La fecha {fecha} no puede ser en el pasado'
                            }), 400
                        if fin <= inicio:
                            return jsonify({
                                'error': f'La hora fin debe ser mayor que la hora inicio para {fecha}'
                            }), 400
                        nuevo_horario = Horario(
                            id_medico=id_medico,
                            dia_semana=fecha_str,
                            hora_inicio=inicio,
                            hora_salida=fin,
                            activo=True
                        )
                        db.session.add(nuevo_horario)
                    
                    db.session.commit()
                    print("=== SCHEDULES SAVED SUCCESSFULLY ===")
                    return jsonify({
                        'message': 'Horarios guardados exitosamente',
                        'details': {
                            'doctor_id': id_medico,
                            'schedule_count': len(horarios)
                        }
                    }), 200
                except Exception as e:
                    db.session.rollback()
                    print(f"Error inserting schedules: {str(e)}")
                    return jsonify({
                        'error': 'Error al insertar nuevos horarios',
                        'details': str(e)
                    }), 500
            except Exception as e:
                print(f"=== ERROR SAVING SCHEDULES ===")
                print(f"Error message: {str(e)}")
                print("=== END ERROR ===")
                return jsonify({
                    'error': str(e),
                    'details': {
                        'received_data': data,
                        'error_type': type(e).__name__
                    }
                }), 400
        except Exception as e:
            print(f"=== ERROR SAVING SCHEDULES ===")
            print(f"Error message: {str(e)}")
            print("=== END ERROR ===")
            return jsonify({
                'error': str(e),
                'details': {
                    'received_data': data,
                    'error_type': type(e).__name__
                }
            }), 400
    except Exception as e:
        print(f"=== UNEXPECTED ERROR ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print(f"Error details: {e.__dict__}")
        print("=== END ERROR ===")
        
        # Try to get more detailed error information
        if isinstance(e, SQLAlchemyError):
            db_error = str(e.orig) if hasattr(e, 'orig') else str(e)
            print(f"Database error details: {db_error}")
            return jsonify({
                'error': 'Error de base de datos',
                'details': {
                    'error': db_error,
                    'error_type': type(e).__name__
                }
            }), 500
        
        # Return a proper JSON response for unexpected errors
        return jsonify({
            'error': 'Error inesperado al guardar los horarios',
            'details': {
                'error': str(e),
                'error_type': type(e).__name__
            }
        }), 500

@app.route('/login_medico', methods=['GET', 'POST'])
def login_medico():
    form = LoginForm()
    if form.validate_on_submit():
        correo = form.username.data
        contrasena = form.password.data
        try:
            print(f"Buscando usuario con correo: {correo}")
            user = db.session.execute(
                select(User).where(User.correo == correo)
            ).scalar_one_or_none()
            if user:
                print(f"Usuario encontrado: {user.correo} (ID: {user.id_usuario})")
                print(f"Detalles del usuario: {user.__dict__}")
                if user.check_password(contrasena):
                    print("Contraseña válida")
                    try:
                        # Verificar si el usuario tiene el rol de Secretario_Medico (id_rol=2)
                        secretario_rol = db.session.execute(
                            select(Role).where(Role.id_rol == 2)
                        ).scalar_one_or_none()
                        if secretario_rol and secretario_rol in user.roles:
                            print("Usuario es Secretario_Medico")
                            session.clear()
                            session['tipo_usuario'] = 'Secretario_Medico'
                            session['user_id'] = user.id_usuario
                            login_user(user)
                            # Buscar el objeto Medico y guardar su id en la sesión
                            medico = db.session.query(Medico).filter_by(id_usuario=user.id_usuario, activo=True).first()
                            if medico:
                                session['medico_id'] = medico.id_medico
                            else:
                                flash('No existe un médico activo asociado a este usuario.', 'error')
                                return render_template('login_medico.html', form=form)
                            db.session.commit()
                            flash('Inicio de sesión exitoso como Secretario Médico.', 'success')
                            return redirect(url_for('dashboard_medico'))
                        else:
                            print("No es Secretario_Medico")
                            flash('No tiene permisos de Secretario Médico.', 'error')
                            return render_template('login_medico.html', form=form)
                    except Exception as e:
                        print(f"Error en la verificación de rol: {str(e)}")
                        flash('Error al verificar el rol.', 'error')
                        return render_template('login_medico.html', form=form)
                else:
                    print("Contraseña inválida")
                    flash('Contraseña incorrecta.', 'error')
                    return render_template('login_medico.html', form=form)
            else:
                print("Usuario no encontrado")
                flash('Correo no registrado como Secretario Médico.', 'error')
                return render_template('login_medico.html', form=form)
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            flash('Error inesperado al iniciar sesión.')
            return render_template('login_medico.html', form=form)
    return render_template('login_medico.html', form=form)

@app.route('/dashboard_medico')
def dashboard_medico():
    id_medico = session.get('medico_id')
    if not id_medico:
        flash('Debe iniciar sesión como médico.', 'error')
        return redirect(url_for('login_medico'))

    # Obtener datos del médico y usuario
    medico = db.session.query(Medico).filter_by(id_medico=id_medico).first()
    if not medico:
        flash('Médico no encontrado.', 'error')
        return redirect(url_for('login_medico'))
    usuario = db.session.query(User).filter_by(id_usuario=medico.id_usuario).first()
    especialidad = db.session.query(Especialidades).filter_by(id_especialidad=medico.id_especialidad).first()

    # Contar citas de hoy para este médico
    total_citas_hoy = db.session.execute(
        text('SELECT COUNT(*) FROM citas WHERE id_medico=:id AND DATE(hora_cita_inicio)=:hoy'),
        {'id': id_medico, 'hoy': datetime.datetime.now().date()}
    ).scalar()

    # Contar permisos activos (licencias activas asociadas a este médico)
    permisos_activos = db.session.execute(
        text('SELECT COUNT(*) FROM licencias l JOIN atenciones a ON l.id_licencia=a.id_atencion WHERE a.id_medico=:id AND l.activo=TRUE'),
        {'id': id_medico}
    ).scalar()

    # Cambios de horario (puedes ajustar la lógica según tu modelo de cambios de horario)
    cambios_horario = db.session.query(Horario).filter_by(id_medico=id_medico, activo=True).count()

    # Contar retroalimentaciones pendientes (estado 'Pendiente')
    retro_pendiente = db.session.query(Retroalimentacion).filter_by(id_medico=id_medico, estado='Pendiente').count()

    # Obtener las próximas 3 citas del médico para hoy
    proximas_citas = db.session.execute(
        text('''
            SELECT c.hora_cita_inicio, c.motivo_cita, 
                   u.nombre AS nombre_paciente, 
                   u.ap_paterno AS appaterno_paciente, 
                   u.ap_materno AS apmaterno_paciente
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            WHERE c.id_medico = :id AND DATE(c.hora_cita_inicio) = :hoy
            ORDER BY c.hora_cita_inicio ASC
            LIMIT 3
        '''),
        {'id': id_medico, 'hoy': datetime.datetime.now().date()}
    ).fetchall()
    citas_list = []
    for c in proximas_citas:
        citas_list.append({
            'hora': c.hora_cita_inicio if hasattr(c, 'hora_cita_inicio') else c[0],
            'motivo': c.motivo_cita if hasattr(c, 'motivo_cita') else c[1],
            'nombre_paciente': c.nombre_paciente if hasattr(c, 'nombre_paciente') else c[2],
            'appaterno_paciente': c.appaterno_paciente if hasattr(c, 'appaterno_paciente') else c[3],
            'apmaterno_paciente': c.apmaterno_paciente if hasattr(c, 'apmaterno_paciente') else c[4],
        })

    return render_template(
        'dashboard_medico.html',
        nombre=usuario.nombre,
        apPaterno=usuario.ap_paterno,
        apMaterno=usuario.ap_materno,
        especialidad=especialidad.nom_espe if especialidad else '',
        certificacion=medico.certificacion,
        cambios_horario=cambios_horario,
        permisos_activos=permisos_activos,
        pacientes_atendidos=total_citas_hoy,
        retro_pendiente=retro_pendiente,
        proximas_citas=citas_list
    )

@app.route('/cambios_horario')
def cambios_horario():
    id_medico = session.get('medico_id')
    if not id_medico:
        flash('Debe iniciar sesión como médico.', 'error')
        return redirect(url_for('login_medico'))
    # Obtener los horarios del médico
    horarios = db.session.query(Horario).filter_by(id_medico=id_medico, activo=True).all()
    # Preparar los datos para el calendario (puedes adaptar el formato según tu JS)
    horarios_list = []
    for h in horarios:
        # Convertir siempre a DD/MM/YYYY
        if hasattr(h.dia_semana, 'strftime'):
            fecha_str = h.dia_semana.strftime('%d/%m/%Y')
        else:
            try:
                partes = h.dia_semana.split('-')
                if len(partes) == 3:
                    fecha_str = f"{partes[2]}/{partes[1]}/{partes[0]}"
                else:
                    fecha_str = h.dia_semana
            except Exception:
                fecha_str = h.dia_semana
        horarios_list.append({
            'fecha': fecha_str,
            'horaInicio': h.hora_inicio.strftime('%H:%M'),
            'horaFin': h.hora_salida.strftime('%H:%M')
        })
    return render_template('cambios_horario.html', horarios=horarios_list)

@app.route('/gestion_permiso')
def gestion_permiso():
    id_medico = session.get('medico_id')
    if not id_medico:
        flash('Debe iniciar sesión como médico.', 'error')
        return redirect(url_for('login_medico'))
    licencias_raw = db.session.execute(
        text('''
            SELECT l.id_licencia, l.fecha_emicion, l.duracion_licencia, l.activo, a.fecha_atencion,
                   p.id_paciente, u.nombre AS nombre_paciente, u.ap_paterno AS appaterno_paciente, u.ap_materno AS apmaterno_paciente, c.motivo_cita
            FROM licencias l
            JOIN atenciones a ON l.id_licencia = a.id_atencion
            JOIN pacientes p ON a.id_historial = p.id_paciente
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            JOIN citas c ON a.id_atencion = c.id_cita
            WHERE a.id_medico = :id AND l.activo = TRUE
            ORDER BY l.fecha_emicion DESC
        '''),
        {'id': id_medico}
    ).fetchall()
    print('--- LICENCIAS RAW ---')
    for l in licencias_raw:
        print(dict(l._mapping) if hasattr(l, '_mapping') else l)
    licencias = []
    for l in licencias_raw:
        fecha_inicio = l.fecinicio if hasattr(l, 'fecinicio') else l[1]
        duracion = l.duracionlicencia if hasattr(l, 'duracionlicencia') else l[2]
        fecha_fin = None
        if fecha_inicio and duracion:
            fecha_fin = fecha_inicio + timedelta(days=int(duracion))
        licencia_dict = {
            'idlicencia': l.idlicencia if hasattr(l, 'idlicencia') else l[0],
            'fecatencion': l.fecatencion if hasattr(l, 'fecatencion') else l[4],
            'nombre_paciente': l.nombre_paciente if hasattr(l, 'nombre_paciente') else l[6],
            'appaterno_paciente': l.appaterno_paciente if hasattr(l, 'appaterno_paciente') else l[7],
            'apmaterno_paciente': l.apmaterno_paciente if hasattr(l, 'apmaterno_paciente') else l[8],
            'motivocita': l.motivocita if hasattr(l, 'motivocita') else l[9],
            'fecinicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'duracionlicencia': duracion,
            'activo': l.activo if hasattr(l, 'activo') else l[3]
        }
        print('Licencia procesada:', licencia_dict)
        licencias.append(licencia_dict)
    print('--- LICENCIAS PROCESADAS ---')
    for lic in licencias:
        print(lic)
    return render_template('gestion_permiso.html', licencias=licencias)

@app.route('/pacientes_atendidos')
def pacientes_atendidos():
    id_medico = session.get('medico_id')
    if not id_medico:
        flash('Debe iniciar sesión como médico.', 'error')
        return redirect(url_for('login_medico'))
    # Obtener pacientes atendidos por el médico
    atenciones_raw = db.session.execute(
        text('''
            SELECT a.fecha_atencion, u.nombre AS nombre_paciente, u.ap_paterno AS appaterno_paciente, u.ap_materno AS apmaterno_paciente, c.motivo_cita, a.id_atencion, a.activo
            FROM atenciones a
            JOIN pacientes p ON a.id_historial = p.id_paciente
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            JOIN citas c ON a.id_atencion = c.id_cita
            WHERE a.id_medico = :id
            ORDER BY a.fecha_atencion DESC
        '''),
        {'id': id_medico}
    ).fetchall()
    atenciones = []
    for a in atenciones_raw:
        atenciones.append({
            'fecatencion': a.fecatencion if hasattr(a, 'fecatencion') else a[0],
            'nombre_paciente': a.nombre_paciente if hasattr(a, 'nombre_paciente') else a[1],
            'appaterno_paciente': a.appaterno_paciente if hasattr(a, 'appaterno_paciente') else a[2],
            'apmaterno_paciente': a.apmaterno_paciente if hasattr(a, 'apmaterno_paciente') else a[3],
            'motivocita': a.motivocita if hasattr(a, 'motivocita') else a[4],
            'idatencion': a.idatencion if hasattr(a, 'idatencion') else a[5],
            'activo': a.activo if hasattr(a, 'activo') else a[6]
        })
    return render_template('pacientes_atendidos.html', atenciones=atenciones)

@app.route('/retroalimentacion', methods=['GET', 'POST'])
def retroalimentacion():
    from app.models.retroalimentacion import Retroalimentacion
    from app.models.medico import Medico
    
    if request.method == 'POST':
        mensaje = request.form.get('mensaje')
        tipo = request.form.get('tipo')
        if mensaje and tipo:
            # Obtener el médico actual
            medico = db.session.query(Medico).filter_by(usuario=current_user).first()
            if medico:
                # Crear nueva retroalimentación
                retro = Retroalimentacion(
                    tipo=str(tipo),  # Guardar como string
                    mensaje=mensaje,
                    id_medico=medico.id_medico
                )
                db.session.add(retro)
                db.session.commit()
                flash('¡Retroalimentación enviada correctamente!', 'success')
            else:
                flash('No se pudo encontrar el médico asociado', 'error')
            return redirect(url_for('retroalimentacion'))
    
    # Obtener todas las retroalimentaciones del doctor actual
    medico = db.session.query(Medico).filter_by(usuario=current_user).first()
    if medico:
        retro_list = db.session.query(Retroalimentacion).filter_by(id_medico=medico.id_medico).order_by(Retroalimentacion.fecha.desc()).all()
    else:
        retro_list = []
    
    return render_template('retroalimentacion.html', retro_list=retro_list)

@app.route('/agenda_medico')
def agenda_medico():
    id_medico = session.get('medico_id')
    if not id_medico:
        flash('Debe iniciar sesión como médico.', 'error')
        return redirect(url_for('login_medico'))
    # Obtener las citas del médico con nombres correctos de tablas y columnas
    citas = db.session.execute(
        text('''
            SELECT c.id_cita, c.hora_cita_inicio, c.hora_cita_termino, c.motivo_cita, u.nombre AS nombre_paciente, u.ap_paterno AS appaterno_paciente, u.ap_materno AS apmaterno_paciente
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            WHERE c.id_medico = :id_medico
            ORDER BY c.hora_cita_inicio ASC
        '''),
        {'id_medico': id_medico}
    ).fetchall()
    # Convertir a lista de dicts para el template y el calendario
    citas_list = []
    for c in citas:
        # hora_cita_inicio y hora_cita_termino son tipo datetime
        inicio = c.hora_cita_inicio if hasattr(c, 'hora_cita_inicio') else c[1]
        fin = c.hora_cita_termino if hasattr(c, 'hora_cita_termino') else c[2]
        citas_list.append({
            'id': c.id_cita if hasattr(c, 'id_cita') else c[0],
            'inicio': inicio.isoformat() if hasattr(inicio, 'isoformat') else str(inicio),
            'fin': fin.isoformat() if hasattr(fin, 'isoformat') else str(fin),
            'motivo': c.motivo_cita if hasattr(c, 'motivo_cita') else c[3],
            'nombre_paciente': c.nombre_paciente if hasattr(c, 'nombre_paciente') else c[4],
            'appaterno_paciente': c.appaterno_paciente if hasattr(c, 'appaterno_paciente') else c[5],
            'apmaterno_paciente': c.apmaterno_paciente if hasattr(c, 'apmaterno_paciente') else c[6],
        })
    return render_template('agenda_medico.html', citas=citas_list)

@app.route('/citas')
@login_required
def citas():
    return render_template('citas.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
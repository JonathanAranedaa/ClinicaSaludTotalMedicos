from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField('Correo', validators=[DataRequired(), Email()], render_kw={'autocomplete': 'username'})
    password = PasswordField('Contraseña', validators=[DataRequired()], render_kw={'autocomplete': 'current-password'})

class MedicoForm(FlaskForm):
    rut = StringField('RUT', validators=[DataRequired(), Length(min=8, max=10)])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apPaterno = StringField('Apellido Paterno', validators=[DataRequired()])
    apMaterno = StringField('Apellido Materno', validators=[DataRequired()])
    sexo = BooleanField('Sexo (Masculino)')
    direccion = StringField('Dirección', validators=[DataRequired()])
    correo = StringField('Correo', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    contrasena = StringField('Contraseña', render_kw={'readonly': True})
    certificacion = StringField('Certificación', validators=[DataRequired()])
    idespecialidad = SelectField('Especialidad', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.rut.data:
            # Generar contraseña: rut sin dígito verificador
            rut_sin_dv = self.rut.data[:-2] if len(self.rut.data) > 2 else self.rut.data
            self.contrasena.data = rut_sin_dv
            
        if not self.correo.data and self.nombre.data and self.apPaterno.data:
            # Generar correo: primeras 2 letras del nombre + . + apellido + primera letra del segundo apellido + @saludtotal.com
            nombre_part = self.nombre.data[:2].lower()
            ap_paterno = self.apPaterno.data.lower()
            ap_materno_first = self.apMaterno.data[0].lower() if self.apMaterno.data else ''
            self.correo.data = f"{nombre_part}.{ap_paterno}{ap_materno_first}@saludtotal.com"

class EliminarMedicoForm(FlaskForm):
    submit = SubmitField('Eliminar')

class EditarMedicoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apPaterno = StringField('Apellido Paterno', validators=[DataRequired()])
    apMaterno = StringField('Apellido Materno', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    certificacion = StringField('Certificación', validators=[DataRequired()])
    idespecialidad = SelectField('Especialidad', coerce=int, validators=[DataRequired()])
    activo = BooleanField('Activo')
    submit = SubmitField('Guardar Cambios')

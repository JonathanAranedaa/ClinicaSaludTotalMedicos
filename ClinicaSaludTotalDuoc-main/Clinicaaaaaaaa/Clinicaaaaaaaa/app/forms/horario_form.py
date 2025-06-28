from flask_wtf import FlaskForm
from wtforms import TimeField, BooleanField, HiddenField, StringField
from wtforms.validators import DataRequired

class HorarioForm(FlaskForm):
    fecha_inicio = HiddenField('Fecha Inicio', validators=[DataRequired()])
    fecha_fin = HiddenField('Fecha Fin', validators=[DataRequired()])
    hora_inicio = TimeField('Hora Inicio', validators=[DataRequired()])
    hora_fin = TimeField('Hora Fin', validators=[DataRequired()])
    activo = BooleanField('Activo', default=True)
    idmedico = HiddenField('ID Médico', validators=[DataRequired()])

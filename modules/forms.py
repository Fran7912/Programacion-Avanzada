from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, Length

class RegisterForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    claustro = SelectField('Claustro', choices=[('Estudiante','Estudiante'),('Docente','Docente'),('PAyS','PAyS')])
    nombre_usuario = StringField('Nombre de Usuario', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    contraseña = PasswordField(label='Contraseña', validators=[DataRequired(), Length(min=8), EqualTo('confirmar_contraseña', message='Las contraseñas deben coincidir')])
    confirmar_contraseña = PasswordField(label='Repetir contraseña', validators=[DataRequired()])
    enviar = SubmitField(label='Registrarse')

class LoginForm(FlaskForm):
    nombre_usuario = StringField(label='Nombre de Usuario', validators=[DataRequired()])
    contraseña = PasswordField(label='Password', validators=[DataRequired(), Length(min=8)])
    enviar = SubmitField(label='Log In')


class FormularioCrearReclamo(FlaskForm):
    titulo = StringField(label='Título del Reclamo', validators=[DataRequired()])
    descripcion=TextAreaField(label='Descripción del Reclamo', validators=[DataRequired(), Length(max=1000)])
    imagen = FileField(label='Insertar Imagen (Opcional)')
    enviar = SubmitField(label='Crear Reclamo')


class FormularioEditarReclamo(FlaskForm):
    estado = SelectField('Estado', choices=[('pendiente','pendiente'),('en proceso','en proceso'),('resuelto','resuelto'),('inválido','inválido')])
    enviar = SubmitField(label='Aceptar')

class ParaSecretarioTecnico(FlaskForm):
    estado = SelectField('Estado', choices=[('pendiente','pendiente'),('en proceso','en proceso'),('resuelto','resuelto'),('inválido','inválido')])
    departamento = SelectField('Departamento', choices=[('secretaría técnica','secretaría técnica'),('soporte informático','soporte informático'),('maestranza','maestranza')])
    enviar = SubmitField(label='Aceptar')
    
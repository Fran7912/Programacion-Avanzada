from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

adhesiones = db.Table('adhesiones',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id')),
    db.Column('reclamo_id', db.Integer, db.ForeignKey('reclamo.id'))
)

class Usuario(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
   
    _nombre = db.Column(db.String(50), nullable=False)
    _apellido = db.Column(db.String(50), nullable=False)
    _email = db.Column(db.String(120), unique=True, nullable=False) 
    _nombre_usuario = db.Column(db.String(50), unique=True, nullable=False) 
    _contraseña = db.Column(db.String(200), nullable=False)
    
    rol = db.Column(db.String(20)) # 'final', 'jefe', 'secretario' (Para manejar la herencia)


    @property
    def id(self):
        return self._id

    @property
    def nombre_usuario(self):
        return self._nombre_usuario


    @property
    def contraseña(self):
        return self._contraseña

   
    @property
    def email(self):
        return self._email    

    @property
    def nombre(self):
        return self._nombre
    
    @property
    def apellido(self):
        return self._apellido

class Reclamo(db.Model):

    _id = db.Column(db.Integer, primary_key=True)

    _titulo = db.Column(db.String(100), nullable=False)
    _descripcion = db.Column(db.Text, nullable=False) 
    _estado = db.Column(db.String(20), default='pendiente') 
    _fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    _imagen = db.Column(db.String(120)) 
    
    # Claves foráneas
    departamento_id = db.Column(db.Integer, nullable=False) 
    autor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    
    # Relación con la tabla de adhesiones
    adherentes = db.relationship('Usuario', secondary=adhesiones, backref='reclamos_adheridos')

from modules.config import db
from sqlalchemy import Column, Integer, String, TIMESTAMP, Float, ForeignKey, Text, DateTime
from flask_login import UserMixin, logout_user
from sqlalchemy.orm import relationship


asociacion_usuarios_reclamos=db.Table('adheridos',
                                      Column('id_usuario', Integer, ForeignKey('usuarios.id')),
                                      Column('id_reclamo', Integer, ForeignKey('reclamos.id')))

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    _id = Column('id', Integer(), primary_key=True)

    _email = Column('email', String(100), unique=True)
    _nombre_usuario = Column('nombre_usuario', String(100), unique=True)
    _contraseña = Column('contraseña', String(100))

    _nombre = Column('nombre', String(100))
    _apellido = Column('apellido', String(100))
    
    _reclamos_seguidos = relationship("Reclamo", secondary=asociacion_usuarios_reclamos, backref="usuarios")

    def __init__(self, Nombre, Apellido, email, nombre_usuario, contraseña):
        self._email = email
        self._nombre_usuario = nombre_usuario
        self._contraseña=contraseña
        self._nombre=Nombre
        self._apellido=Apellido


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
    __tablename__='reclamos'

    _id = Column('id', Integer(), primary_key=True)

    _autor=Column('autor', Integer())
    _departamento = Column('departamento', String(100))

    _fecha = Column('fecha', String(30)) #verificar si funciona así
    _estado = Column('estado', String(100))
    _titulo=Column('titulo', String (100))
    _descripcion = Column('descripcion', String(10000))

    _imagen= Column('imagen', String(100))
    #imagen = db.relationship('Imagen', secondary=imagen_reclamo, backref='reclamo')


    def __init__(self,autor, departamento, fecha, estado, titulo, descripcion):
        
        self._autor = autor
        self._departamento = departamento
        self._fecha = fecha
        self._estado = estado
        self._titulo = titulo
        self._descripcion = descripcion

    def __str__(self): 
        reclamo = f"Titulo: {self.Titulo} \nDescripción: {self.Descripcion}"
        return reclamo
    
    @property
    def id(self):
        return self._id
    @property
    def autor(self):
        return self._autor
    @property
    def departamento(self):
        return self._departamento
    @property
    def fecha(self):
        return self._fecha
    @property
    def estado(self):
        return self._estado
    @property
    def titulo(self):
        return self._titulo
    @property
    def descripcion(self):
        return self._descripcion
    @property
    def imagen(self):
        return self._imagen

    
    @imagen.setter
    def imagen(self, imagen):
        self._imagen = imagen


    @estado.setter
    def estado(self, nuevo_estado):
        if nuevo_estado in ['pendiente', 'inválido', 'en proceso', 'resuelto']:
            self._estado = nuevo_estado
        else:
            raise Exception

    @departamento.setter
    def departamento(self, nuevo_departamento):
        if nuevo_departamento in ['secretaría técnica','soporte informático','maestranza']:
            self._departamento = nuevo_departamento
        else:
            raise Exception





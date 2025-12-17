from modules.config import db
from modules.databases import Usuario, Column, String, asociacion_usuarios_reclamos


class UsuarioFinal(Usuario): 
    _claustro = Column('claustro', String(100)) 
    _reclamos_adheridos = db.relationship('Reclamo', secondary=asociacion_usuarios_reclamos, backref='usuarios_adheridos')

    def __init__(self, nombre, apellido, email, nombre_usuario, contraseña, claustro): 
        super().__init__(nombre, apellido, email, nombre_usuario, contraseña) 
        self._claustro = claustro


    @property 
    def claustro(self): 
           return self._claustro
    @property
    def reclamos_adheridos(self):
        return self._reclamos_adheridos

    def adherir_a_reclamo(self, reclamo): 
        self._reclamos_adheridos.append(reclamo)
        

class JefeDeDepartamento(Usuario): 
    _departamento = Column('departamento', String(100)) 


    def __init__(self,Nombre,Apellido,email,nombre_usuario, contraseña, Departamento): 
        super().__init__(Nombre,Apellido,email,nombre_usuario, contraseña)
        self._departamento = Departamento

    @property 
    def departamento(self): 
           return self._departamento
    
    

from modules.config import db
from modules.databases import Usuario, Column, String, asociacion_usuarios_reclamos


class UsuarioFinal(Usuario): 
    _claustro = = Column('claustro', String(100))
    
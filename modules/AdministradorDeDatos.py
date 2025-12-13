import numpy as np
from datetime import datetime
from mimetypes import guess_type
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, current_user
from flask import session
from modules.forms import RegisterForm, LoginForm
from modules.config import db, images
from modules.databases import Usuario, Reclamo
from modules.Usuario import UsuarioFinal, JefeDeDepartamento
from modules.clasificador import Clasificador
from modules.preprocesamiento import ProcesadorArchivo

class AdministradorDeDatos: 

    def __init__(self, db):
        self._jefes = [1,2,3]
        self._reclamo = {} 
        self._db = db

        self._procesador = ProcesadorArchivo("frases.json")
        self.x,self.y=self._procesador.datosEntrenamiento

        self._clasificador = Clasificador(self.x,self.y, escalado=True)

    @property
    def jefes(self):
        return self._jefes        

    @property
    def reclamo(self):
        return self._reclamo
        
    @property
    def procesador(self):
        return self._procesador
        
    @property
    def Clasificador(self):
        return self._Clasificador

    @property
    def db(self):
        return self._db

    def guardar_usuario(self, email, nombre_usuario, contraseña, Nombre, Apellido, claustro):
        """Verifica que los datos ingresados para el registro sean válidos y los guarda en la base de datos,
          devuelve el formulario del registro)"""    
        
        info = "usuario guardado exitosamente"
        
        if Usuario.query.filter(UsuarioFinal.__table__.c.nombre_usuario == email).first():
            info = "Ese correo electrónico ya está siendo utilizado."
        elif Usuario.query.filter(UsuarioFinal.__table__.c.nombre_usuario == nombre_usuario).first():
            info = "El nombre de usuario ya está siendo utilizado."
        else:
            contraseña_encriptada = generate_password_hash(password= contraseña, 
                                                           method= 'pbkdf2:sha256', 
                                                           salt_length=8)                           #Se encripta la contraseña

            usuario = UsuarioFinal(email = email, 
                                   nombre_usuario = nombre_usuario, 
                                   contraseña = contraseña_encriptada, 
                                   Nombre = Nombre, 
                                   Apellido = Apellido, 
                                   claustro = claustro)  #se crea al usuario 

            self._db.session.add(usuario)
            self._db.session.commit()

        return info
        
    def cargar_usuario(self,nombre_usuario, contraseña):
        """Carga un usuario de la base de datos según su nombre de usuario."""
        funcion = "inicio_para_usuario_final"

        usuario = Usuario.query.filter(UsuarioFinal.__table__.c.nombre_usuario == nombre_usuario).first()
        if not usuario:
            usuario = JefeDepartamento.query.filter(JefeDepartamento.__table__.c.nombre_usuario == nombre_usuario).first()
        if not usuario: 
            funcion = "No se encontró el usuario."
           
        elif check_password_hash(usuario.contraseña , contraseña):
            return usuario, funcion
        
        usuario = None 
        return usuario, funcion

    def crear_reclamo(self):  
        """Crea un nuevo reclamo y lo guarda en la base de datos."""
        rec = Reclamo(autor= self._reclamo.get('autor'),
                      departamento= self._reclamo.get('departamento'),
                      fecha = self._reclamo.get('fecha'),
                      estado= self._reclamo.get('estado'),
                      titulo= self._reclamo.get('titulo'),
                      descripcion= self._reclamo.get('descripcion')                  
                      )
        if self._reclamo.get('imagen'):
            rec.imagen = self._reclamo.get('imagen')
        
        self._db.session.add(rec)
        self._db.session.commit()
        
        
    def obtener_reclamos(self, departamento):
        """Obtiene todos los reclamos de la base de datos."""
        reclamos = Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento).all()
        return reclamos
    def adherir_usuario(self,usuario, reclamo_id):
        """Adhiere un usuario a un reclamo específico."""
        reclamo = Reclamo.query.get(reclamo_id)
        usuario.adherir_reclamo(reclamo)
        self._db.session.commit()
    
    def buscar_similares(self, texto):
        """Busca reclamos similares al texto proporcionado."""
        texto = self._reclamo.get('titulo')
        vacio = stopwords.words('spanish')
        text_tokens = word_tokenize(texto.lower())

        p_clave = [palabra for palabra in text_tokens if palabra not in vacio and len(palabra)>=4]

        resultados =[]

        for p_clave in p_clave: 
            reclamos_similares = Reclamo.query.filter(Reclamo.__table__.c.descripcion.like(f'%{p_clave}%')).all() #busca similares segun descripción
            for reclamo in reclamos_similares:
                if reclamo not in resultados:
                    resultados.append(reclamo)

        return resultados
    
    def obtener_reclamo_departamento_estado(self, departamento, estado):
        """devuelve listas de  reclamos filtrados por departamento y estado."""
        reclamos_en_proceso=list(Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento , Reclamo.__table__.c.estado == "en proceso").all())
        reclamos_pendiente=list(Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento , Reclamo.__table__.c.estado == "pendiente").all())
        reclamos_resuelto=list(Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento , Reclamo.__table__.c.estado == "resuelto").all())
        reclamos_invalido=list(Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento , Reclamo.__table__.c.estado == "inválido").all())
        
        return reclamos_en_proceso, reclamos_pendiente, reclamos_resuelto, reclamos_invalido

    
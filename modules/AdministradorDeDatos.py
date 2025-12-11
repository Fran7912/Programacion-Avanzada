from datetime import datetime
from mimetypes import guess_type
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


from modules.config import db, images


from modules.forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, current_user
from flask import session


from modules.databases import Usuario, Reclamo
from modules.Usuario import UsuarioFinal, JefeDepartamento
from modules.clasificador import Clasificador
from modules.preprocesamiento import ProcesadorArchivo

class AdministradorDeDatos: 

    def __init__(self, db):
        self._jefes = [1,2,3]
        self._reclamo = {} 
        self._db = db

        self._procesador = ProcesadorArchivos("frases.json")
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
        pass
    def cargar_usuario(self,nombre_usuario, contraseña):
        """Carga un usuario de la base de datos según su nombre de usuario."""
        pass
    def crear_reclamo(self):  
        """Crea un nuevo reclamo y lo guarda en la base de datos."""
        pass
    def obtener_reclamos(self):
        """Obtiene todos los reclamos de la base de datos."""
        pass
    def adherir_usuario(self,usuario, reclamo_id):
        """Adhiere un usuario a un reclamo específico."""
        pass
    def buscar_similares(self, texto):
        """Busca reclamos similares al texto proporcionado."""
        pass
    def obtener_reclamo_departamento_estado(self, departamento, estado):
        """devuelve listas de  reclamos filtrados por departamento y estado."""
        pass

    
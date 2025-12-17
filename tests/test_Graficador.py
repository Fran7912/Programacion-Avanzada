import unittest
import tempfile
from sqlalchemy.orm import Session
from flask import Flask
from flask_login import LoginManager, login_user
from datetime import timedelta
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash
from modules.databases import Reclamo
from modules.Usuario import UsuarioFinal,JefeDeDepartamento
from modules.AdministradorDeDatos import AdministradorDeDatos  
from modules.config import db, TestingConfig, DevelopmentConfig
from modules.preprocesamiento import ProcesadorArchivo
from modules.clasificador import Clasificador
from modules.databases import Reclamo
from modules.Usuario import UsuarioFinal,JefeDeDepartamento
from modules.config import db, TestingConfig, DevelopmentConfig
from modules.informante import InformantePDF, InformanteHTML, GraficadorDiagramaCircular, GraficadorPalabrasClave
import os

def create_app(config_name="development"):

    """Crea y configura la instancia de la aplicación Flask."""
    
    app = Flask(__name__)
    Session(app) 
    login_manager=LoginManager()
    images=UploadSet('images', IMAGES)

        # Configuración de la app según el entorno
    app.config['SECRET_KEY'] = 'loquemasteguste'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["UPLOADED_IMAGES_DEST"] = "src/static/uploads/images"
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


    config_classes = {
    "development": DevelopmentConfig,
    "testing": TestingConfig
    }

    # Aplicar la configuración correcta
    app.config.from_object(config_classes.get(config_name, DevelopmentConfig))

    # Inicializar las extensiones con la app
    db.init_app(app)

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return JefeDeDepartamento

        
    configure_uploads(app, images)
    return app

class TestGraficadores (unittest.TestCase):
    def setUp(self):
        """ Configuración antes de cada test """
        self.app = create_app('testing')  
        self.client = self.app.test_client()  
        self.app_context=self.app.app_context()
        self.app_context.push()
        
        db.create_all()  
        self.temp_dir = tempfile.TemporaryDirectory()

        self.diagramas_dir = os.path.join(self.temp_dir.name, "..", "static", "diagramas")
        os.makedirs(self.diagramas_dir, exist_ok=True)

    def tearDown(self):
        """ Limpieza después de cada test """
        
        db.session.remove()
        db.drop_all() 
        self.app_context.pop()
        self.temp_dir.cleanup()


    def test_generar_diagrama_circular(self):
        graficador=GraficadorDiagramaCircular()
        admin_datos=AdministradorDeDatos(db)
        reclamo = Reclamo(
            autor="usuario",
            departamento="secretaría técnica",
            fecha="2025/02/27 18:30:34",
            estado="pendiente",
            titulo="Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.",
            descripcion="Está todo oscuro",
        )

        db.session.add(reclamo)
        db.session.commit()

        secretario_tecnico = JefeDeDepartamento(
            email="secretariotecnico@email.com",
            nombre_usuario="Tecnico",
            contraseña=generate_password_hash("12345678"),
            Nombre="Secretario",
            Apellido="Tecnico",
            Departamento="secretaría técnica"
        )
        db.session.add(secretario_tecnico)
        db.session.commit()

        graficador.graficar(admin=admin_datos,departamento=secretario_tecnico.departamento, ruta_base=self.temp_dir.name, tipo='png')
        graficador.graficar(admin=admin_datos,departamento=secretario_tecnico.departamento, ruta_base=self.temp_dir.name, tipo='svg')

        ruta_diagramas = os.path.join(self.temp_dir.name, "..", "static", "diagramas")
        ruta_diagrama = os.path.join(ruta_diagramas, "diagrama_circular_secretaría_técnica.png")
        ruta_diagrama_svg = os.path.join(ruta_diagramas, "diagrama_circular_secretaría_técnica.svg")
        
        ruta_diagrama = os.path.normpath(ruta_diagrama)
        ruta_diagrama_svg = os.path.normpath(ruta_diagrama_svg)
        
    
        # Verificar que los archivos existen
        self.assertTrue(os.path.exists(ruta_diagrama))
        self.assertTrue(os.path.exists(ruta_diagrama_svg))

        # Verificar que los archivos no están vacíos
        self.assertGreater(os.path.getsize(ruta_diagrama), 0)
        self.assertGreater(os.path.getsize(ruta_diagrama_svg), 0)

    def test_generar_diagrama_palabras_clave(self):
        graficador=GraficadorPalabrasClave()
        admin_datos=AdministradorDeDatos(db)
        reclamo = Reclamo(
            autor="usuario",
            departamento="secretaría técnica",
            fecha="2025/02/27 18:30:34",
            estado="pendiente",
            titulo="Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.",
            descripcion="Está todo oscuro",
        )

        db.session.add(reclamo)
        db.session.commit()

        secretario_tecnico = JefeDeDepartamento(
            email="secretariotecnico@email.com",
            nombre_usuario="Tecnico",
            contraseña=generate_password_hash("12345678"),
            Nombre="Secretario",
            Apellido="Tecnico",
            Departamento="secretaría técnica"
        )
        db.session.add(secretario_tecnico)
        db.session.commit()

        graficador.graficar(admin=admin_datos,departamento=secretario_tecnico.departamento, ruta_base=self.temp_dir.name, tipo='png')
        graficador.graficar(admin=admin_datos,departamento=secretario_tecnico.departamento, ruta_base=self.temp_dir.name, tipo='svg')

        ruta_diagramas = os.path.join(self.temp_dir.name, "..", "static", "diagramas")
        ruta_diagrama = os.path.join(ruta_diagramas, "nube_palabras_secretaría_técnica.png")
        ruta_diagrama_svg = os.path.join(ruta_diagramas, "nube_palabras_secretaría_técnica.svg")
        
        ruta_diagrama = os.path.normpath(ruta_diagrama)
        ruta_diagrama_svg = os.path.normpath(ruta_diagrama_svg)
        
    
        # Verificar que los archivos existen
        self.assertTrue(os.path.exists(ruta_diagrama))
        self.assertTrue(os.path.exists(ruta_diagrama_svg))

        # Verificar que los archivos no están vacíos
        self.assertGreater(os.path.getsize(ruta_diagrama), 0)
        self.assertGreater(os.path.getsize(ruta_diagrama_svg), 0)

        


if __name__ == '__main__':
    unittest.main()
   
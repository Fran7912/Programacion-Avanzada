import unittest
import os
from unittest.mock import patch, ANY
import sys
from sqlalchemy.orm import Session
from flask import Flask, send_file
from unittest import TestCase
from flask_login import LoginManager
from datetime import timedelta
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user, login_manager

ruta_actual = os.getcwd()+"/src"

sys.path.append(ruta_actual)
from modules.databases import Reclamo
from modules.Usuario import UsuarioFinal,JefeDeDepartamento
from modules.AdministradorDeDatos import AdministradorDeDatos  
from modules.config import db, TestingConfig, DevelopmentConfig
from modules.informante import InformantePDF, InformanteHTML, GraficadorDiagramaCircular, GraficadorPalabrasClave


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
        return db.session.get(JefeDeDepartamento, int(user_id))
        
    configure_uploads(app, images)
    return app


class TestInformantes(unittest.TestCase):
    def setUp(self):
        """ Configuración antes de cada test """
        
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
   
        @self.app.route("/generar_informe/pdf")
        @login_required
        def generar_informe_pdf():
            admin_datos = AdministradorDeDatos(db)
            informante = InformantePDF(
                graficador_torta=GraficadorDiagramaCircular(),
                graficador_nube=GraficadorPalabrasClave()
            )
            print("🚀 Entrando a la función de generación de PDF...")
            respuesta = informante.generar_informe(departamento=current_user.departamento, admin_datos=admin_datos)
            print(f"Respuesta de la función: {respuesta}")
            return respuesta
            
        @self.app.route("/generar_informe/html")
        @login_required
        def generar_informe_html():
            admin_datos = AdministradorDeDatos(db)
            informante = InformanteHTML(
                graficador_torta=GraficadorDiagramaCircular(),
                graficador_nube=GraficadorPalabrasClave()
            )
            print("Entrando a la función de generación de HTML...")
            
            respuesta = informante.generar_informe(departamento=current_user.departamento, admin_datos=admin_datos)
            print(f"Respuesta de la función: {respuesta}")
            return respuesta

    def tearDown(self):
        """ Limpieza después de cada test """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch("modules.informante.send_file")
    def test_descargar_pdf_mockeado(self, mock_send_file):
        mock_send_file.return_value = "mocked_response"

        # Crear el usuario primero
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

        # Usar el departamento del usuario para el reclamo
        reclamo = Reclamo(
            autor="usuario",
            departamento=secretario_tecnico.departamento,
            fecha="2025/02/27 18:30:34",
            estado="pendiente",
            titulo="Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.",
            descripcion="Está todo en penumbras",
        )
        db.session.add(reclamo)
        db.session.commit()

        print("Rutas registradas en la aplicación de prueba:")
        for rule in self.app.url_map.iter_rules():
            print(rule)

        # Simular login
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(secretario_tecnico.id)
            sess['_fresh'] = True

        response = self.client.get("/generar_informe/pdf")

        print(f"Status code: {response.status_code}")
        print(f"Mock send_file call count: {mock_send_file.call_count}")
        print(f"Mock send_file call args: {mock_send_file.call_args}")

        # Verificar que send_file fue llamado
        self.assertTrue(mock_send_file.called, "send_file no fue llamado")
        
        if mock_send_file.called:
            # Obtener la ruta pasada a send_file (primer argumento posicional)
            ruta_llamada = mock_send_file.call_args[0][0]
            
            # Normalizar ambas rutas para compararlas
            ruta_llamada_normalizada = os.path.normpath(ruta_llamada)
            
            print(f"Ruta llamada normalizada: {ruta_llamada_normalizada}")
            
            # Verificar que send_file fue llamado con los argumentos correctos
            # Usar ANY para ignorar los parámetros adicionales
            mock_send_file.assert_called_once()
            
            # Verificar el primer argumento (la ruta)
            call_args = mock_send_file.call_args
            self.assertTrue(call_args[0][0].endswith('.pdf'), "La ruta no termina en .pdf")
            self.assertEqual(call_args[1]['as_attachment'], True, "as_attachment debe ser True")

    @patch("modules.informante.send_file")
    def test_descargar_html_mockeado(self, mock_send_file):
        mock_send_file.return_value = "mocked_response"

        # Crear el usuario primero
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

        # Usar el departamento del usuario para el reclamo
        reclamo = Reclamo(
            autor="usuario",
            departamento=secretario_tecnico.departamento,
            fecha="2025/02/27 18:30:34",
            estado="pendiente",
            titulo="Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.",
            descripcion="Está todo en penumbras",
        )
        db.session.add(reclamo)
        db.session.commit()

        print("Rutas registradas en la aplicación de prueba:")
        for rule in self.app.url_map.iter_rules():
            print(rule)

        # Simular login
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(secretario_tecnico.id)
            sess['_fresh'] = True

        response = self.client.get("/generar_informe/html")

        print(f"Status code: {response.status_code}")
        print(f"Mock send_file call count: {mock_send_file.call_count}")
        print(f"Mock send_file call args: {mock_send_file.call_args}")

        # Verificar que send_file fue llamado
        self.assertTrue(mock_send_file.called, "send_file no fue llamado")
        
        if mock_send_file.called:
            # Verificar que send_file fue llamado una vez
            mock_send_file.assert_called_once()
            
            # Verificar los argumentos
            call_args = mock_send_file.call_args
            self.assertTrue(call_args[0][0].endswith('.html'), "La ruta no termina en .html")
            self.assertEqual(call_args[1]['as_attachment'], True, "as_attachment debe ser True")


if __name__ == '__main__':
    unittest.main()
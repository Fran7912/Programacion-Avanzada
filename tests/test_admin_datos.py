import unittest
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

class TestAdministradorDeDatos(unittest.TestCase):

    def setUp(self):
        """ Configuración antes de cada test """
        self.app = create_app('testing')  # Inicializa la app en modo testing
        self.client = self.app.test_client()  # Guarda el test_client en self
        self.app_context=self.app.app_context()
        self.app_context.push()
        
        db.create_all()

    def tearDown(self):
        """ Limpieza después de cada test """
        
        db.session.remove()
        db.drop_all()  # Elimina la base de datos
        self.app_context.pop()
   
    def test_init_administrador_de_datos(self):
        admin=AdministradorDeDatos(db)

        self.assertEqual(admin.jefes, [1,2,3])
        self.assertIsInstance(admin.procesador, ProcesadorArchivo)
        self.assertIsInstance(admin.Clasificador, Clasificador)
        self.assertEqual(admin.db, db)
        self.assertEqual(admin.reclamo, {})        
    
    def test_guardar_usuario(self):

        admin = AdministradorDeDatos(db)

        info = admin.guardar_usuario( email= 'usuario@gmail.com',
                                      nombre_usuario= 'usuario123',
                                      contraseña='hashedpassword',
                                      nombre='usuario',
                                      apellido = 'Gonzales',
                                      claustro= 'PAyS' )
        
       
        usuario_registrado=UsuarioFinal.query.filter(UsuarioFinal.__table__.c.nombre_usuario == "usuario123").first()
        
        self.assertEqual(info, "usuario guardado exitosamente")
        self.assertIsNotNone(usuario_registrado)
        self.assertEqual(usuario_registrado.nombre_usuario,'usuario123')
        self.assertEqual(usuario_registrado.email,'usuario@gmail.com')
        self.assertEqual(usuario_registrado.apellido,'Gonzales')
        self.assertEqual(usuario_registrado.claustro, 'PAyS')
        self.assertEqual(usuario_registrado.nombre,'usuario')

    def test_login_usuario_inicia_correctamente(self):

        admin = AdministradorDeDatos(db)
        info = admin.guardar_usuario( email= 'usuario@gmail.com',
                                      nombre_usuario= 'usuario123',
                                      contraseña='hashedpassword',
                                      nombre='usuario',
                                      apellido = 'Gonzales',
                                      claustro= 'PAyS' )
        
        usuario_logueado, funcion= admin.cargar_usuario(nombre_usuario='usuario123',
                                                      contraseña= 'hashedpassword')
        
        self.assertIsNotNone(usuario_logueado)
        self.assertEqual(funcion, "inicio_para_usuario_final")
        self.assertEqual(usuario_logueado.nombre_usuario,'usuario123')
        self.assertEqual(usuario_logueado.email,'usuario@gmail.com')
        self.assertEqual(usuario_logueado.apellido,'Gonzales')
        self.assertEqual(usuario_logueado.nombre,'usuario')
        self.assertEqual(usuario_logueado.claustro, 'PAyS')

    def test_guardar_datos_reclamo_correctamente(self): 
        
        admin = AdministradorDeDatos(db)
        info = admin.guardar_usuario( email= 'usuario@gmail.com',
                                      nombre_usuario= 'usuario123',
                                      contraseña='hashedpassword',
                                      nombre='usuario',
                                      apellido = 'Gonzales',
                                      claustro= 'PAyS' )
        
        usuario_logueado, funcion= admin.cargar_usuario(nombre_usuario='usuario123',
                                                      contraseña= 'hashedpassword')
        
        admin.guardar_datos_reclamo(autor = usuario_logueado.nombre_usuario, 
                                    titulo = 'Se terminó el agua del dispenser de las secretarías.', 
                                    descripcion='Tenemos sed', 
                                    imagen=False)
    
    def test_crear_reclamo_correctamente(self): 
        admin = AdministradorDeDatos(db)
        info = admin.guardar_usuario( email= 'usuario@gmail.com',
                                      nombre_usuario= 'usuario123',
                                      contraseña='hashedpassword',
                                      nombre='usuario',
                                      apellido = 'Gonzales',
                                      claustro= 'PAyS' )
        
        usuario_logueado, funcion= admin.cargar_usuario(nombre_usuario='usuario123',
                                                      contraseña= 'hashedpassword')
        with self.app.test_request_context():
            login_user(usuario_logueado)
            admin.guardar_datos_reclamo(autor = usuario_logueado.nombre_usuario, 
                                        titulo = 'No hay agua en el modulo 3.',        
                                        descripcion='faltan bidones', 
                                        imagen=False)
            admin.crear_reclamo()
        
        reclamo_creado = Reclamo.query.filter(Reclamo.__table__.c.autor == 'usuario123').first()

        self.assertEqual(usuario_logueado.nombre_usuario,reclamo_creado.autor)
        self.assertEqual(reclamo_creado.estado,'pendiente')
        self.assertEqual(reclamo_creado.titulo,'No hay agua en el modulo 3.')
        self.assertEqual(reclamo_creado.descripcion,'faltan bidones')
    
    def test_adherir_usuario(self):
        
        admin=AdministradorDeDatos(db)
        info = admin.guardar_usuario( email= 'usuario@gmail.com',
                                    nombre_usuario= 'usuario123',
                                    contraseña='hashedpassword',
                                    nombre='usuario',
                                    apellido = 'Gonzales',
                                    claustro= 'PAyS' )
        
        autor, funcion = admin.cargar_usuario(nombre_usuario='usuario123',
                                                      contraseña= 'hashedpassword')
        
        info=admin.guardar_usuario(email='otro_usuario@gmail.com', 
                                     nombre_usuario='otro_usuario123', 
                                     contraseña='hashedpassword', 
                                     nombre='otro_usuario', 
                                     apellido='Martinez', 
                                     claustro ='estudiante')
        
        adherido, funcion = admin.cargar_usuario(nombre_usuario='otro_usuario123',
                                                 contraseña='hashedpassword')


        with self.app.test_request_context():
                    
                    login_user(autor)

                    admin.guardar_datos_reclamo(autor = autor.nombre_usuario, 
                                    titulo = 'falta papel en el baño', 
                                    descripcion='no hay papel en el baño del modulo 3', 
                                    imagen=False)
                    admin.crear_reclamo()
        
        
        reclamo_creado = Reclamo.query.filter(Reclamo.__table__.c.titulo == 'falta papel en el baño').first()

        admin.adherir_usuario(usuario = adherido,
                             reclamo_id = reclamo_creado.id)
        
        self.assertIn(reclamo_creado,adherido.reclamos_adheridos)
   
    def test_obtener_reclamo(self): 
        admin=AdministradorDeDatos(db)
        reclamo1 = Reclamo(autor='usuario1', departamento='secretaría técnica', fecha='2025/12/02 16:01:26', estado='pendiente', titulo='Sin luces en el aula 2', descripcion='se quemaron los focos')
        reclamo2 = Reclamo(autor='usuario2', departamento='soporte informático', fecha='2023/23/04 09:38:47', estado='pendiente', titulo='No hay wifi para alumnos.', descripcion='')
        reclamo3 = Reclamo(autor='usuario3', departamento='maestranza', fecha='2024/16/08 14:47:08', estado='pendiente', titulo='No hay jabón en el baño de varones del ala 3.', descripcion='')
        reclamo4 = Reclamo(autor='usuario5', departamento='soporte informático', fecha='2025/12/16 14:15:45', estado='en proceso', titulo='Problema con usuario SIU', descripcion='No puedo ingresar al sistema de gestión para cargar las condiciones finales de los alumnos.')
        reclamo5 = Reclamo(autor='usuario6', departamento='maestranza', fecha='2025/12/16 08:30:12', estado='pendiente', titulo='Falta limpieza Aula 5', descripcion='Se encuentran restos de materiales de una maqueta de la clase anterior que impiden el paso.')

        db.session.add(reclamo1)
        db.session.add(reclamo2)
        db.session.add(reclamo3)
        db.session.add(reclamo4)
        db.session.add(reclamo5)
        db.session.commit()

        reclamos=admin.obtener_reclamos(departamento='secretaría técnica')

        self.assertIsNotNone(reclamos)
        self.assertEqual(len(reclamos),1)
        self.assertEqual(reclamos[0].autor,'usuario1')
        self.assertEqual(reclamos[0].departamento,'secretaría técnica')
        self.assertEqual(reclamos[0].titulo,'Sin luces en el aula 2')
        self.assertEqual(reclamos[0].estado,'pendiente')
        
    def test_buscar_reclamos_similares(self):    
        reclamo1 = Reclamo(autor='Juan', departamento='secretaría técnica', fecha='2025/12/02 16:01:26', estado='pendiente', titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', descripcion='eqw')
        reclamo2 = Reclamo(autor='José', departamento='soporte informático', fecha='2023/23/04 09:38:47', estado='pendiente', titulo='No anda la red wifi de alumnos.', descripcion='eqw')

        db.session.add(reclamo1)
        db.session.add(reclamo2)
        db.session.commit()


        admin=AdministradorDeDatos(db)
        admin.guardar_datos_reclamo(
                                    autor = 'José', 
                                    titulo = 'El aula 3 está algo oscura. Le falta luminosidad.', 
                                    descripcion='Tenemos sed', 
                                    imagen=False)
        reclamos=admin.buscar_reclamos_similares()
        self.assertEqual(len(reclamos),1)
        self.assertEqual(reclamos[0].autor,'Juan')
        self.assertEqual(reclamos[0].departamento,'secretaría técnica')
        self.assertEqual(reclamos[0].titulo,'Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.')
        self.assertEqual(reclamos[0].estado,'pendiente')
        
    def test_obtener_reclamos_departamento_sep_estado(self):
            reclamo1=Reclamo(autor='Juan', 
                             departamento='secretaría técnica', 
                             fecha='2025/12/02 16:01:26', 
                             estado='pendiente', 
                             titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', 
                             descripcion='eqw'
            )
            reclamo2 = Reclamo(autor='Jorge', 
                             departamento='secretaría técnica', 
                             fecha='2025/12/02 16:01:26', 
                             estado='en proceso', 
                             titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', 
                             descripcion='eqw'
            )
            reclamo3 = Reclamo(autor='José', 
                             departamento='secretaría técnica', 
                             fecha='2025/12/02 16:01:26', 
                             estado='resuelto', 
                             titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', 
                             descripcion='eqw'
            )
            reclamo4=Reclamo(autor='Pablo', 
                             departamento='secretaría técnica', 
                             fecha='2025/12/02 16:01:26', 
                             estado='inválido', 
                             titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', 
                             descripcion='eqw'
            )

            db.session.add(reclamo1)
            db.session.add(reclamo2)
            db.session.add(reclamo3)
            db.session.add(reclamo4)
            db.session.commit()

            admin = AdministradorDeDatos(db)

            reclamos_enproceso, reclamos_pendiente, reclamos_resuelto, reclamos_invalido = admin.obtener_reclamos_departamento_estado(departamento='secretaría técnica')

            self.assertEqual(reclamos_enproceso[0].autor, 'Jorge')
            self.assertEqual(reclamos_pendiente[0].autor, 'Juan')
            self.assertEqual(reclamos_resuelto[0].autor, 'José')
            self.assertEqual(reclamos_invalido[0].autor, 'Pablo')
        
if __name__ == '__main__':
    unittest.main()

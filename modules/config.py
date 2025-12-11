from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_uploads import UploadSet, configure_uploads, IMAGES

from datetime import timedelta

app = Flask("app")

app.config['SECRET_KEY'] = 'loquemasteguste'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["WTF_CSRF_ENABLED"] = False

app.config["UPLOADED_IMAGES_DEST"] = "src/static/uploads/images"
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
Session(app)

Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

def create_app(config_name="development"):
    """Crea y configura la instancia de la aplicación Flask."""
    
    app = Flask(__name__)
    session = Session(app) 
    bootstrap=Bootstrap(app)


    # Configuración de la app según el entorno
    app.config['SECRET_KEY'] = 'loquemasteguste'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["UPLOADED_IMAGES_DEST"] = "src/static/uploads/images"
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
    app.config.from_object(f"app.config.{config_name.capitalize()}Config")

    # Inicializar las extensiones con la app
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    configure_uploads(app, images)

    return app

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///datos_dev.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev_secret_key"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Base de datos en memoria para pruebas
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test_secret_key"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    TESTING = True
from flask import render_template,Flask, request, redirect, url_for, session, flash, abort, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from modules.config import app, db, login_manager
from modules.AdministradorDeDatos import AdministradorDeDatos
from modules.Usuario import UsuarioFinal, JefeDeDepartamento
from modules.databases import Reclamo
from modules.forms import RegisterForm, LoginForm, FormularioCrearReclamo, FormularioEditarReclamo, ParaSecretarioTecnico
from werkzeug.security import generate_password_hash
from functools import wraps
from modules.informante import GraficadorDiagramaCircular, GraficadorPalabrasClave, InformantePDF, InformanteHTML


admin_datos = AdministradorDeDatos(db)

Jefes=['1','2','3']

with app.app_context():
    db.create_all()

@login_manager.user_loader
def user_loader(user_id):
    if user_id in Jefes:
        #global graficador_diagrama
        global graficador_nube
        
        #graficador_diagrama=GraficadorDiagramaCircular()
        graficador_nube=GraficadorPalabrasClave()
        return db.session.get(JefeDeDepartamento, user_id)
    else:
        return db.session.get(UsuarioFinal, user_id)


# Restricciones
def solo_jefes(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not isinstance(current_user,JefeDeDepartamento):
            return abort(403)
        return f(*args,**kwargs)
    return decorated_function


def solo_usuarios_finales(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not isinstance(current_user,UsuarioFinal):
            return abort(403)
        return f(*args,**kwargs)
    return decorated_function

#Rutas 

# Página de inicio
@app.route('/')
def inicio():
    return render_template('INICIO.html')

@app.route("/register", methods = ['GET','POST'])
def register():

    register_form=RegisterForm()
    
    if register_form.validate_on_submit():
        info = admin_datos.guardar_usuario(email = register_form.email.data, 
                                             nombre_usuario = register_form.nombre_usuario.data, 
                                             contraseña = register_form.contraseña.data, 
                                             Nombre = register_form.nombre.data, 
                                             Apellido = register_form.apellido.data, 
                                             claustro = register_form.claustro.data)
        
        if info=="Usuario registrado exitosamente, inicie sesión para ingresar":
            flash(info)
            return redirect(url_for("login"))
        else:
            flash(info)
            return render_template("register.html",form=register_form)
            #return render_template("register.html",form=register_form)
    else:
        return render_template("register.html",form=register_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
   
    login_form=LoginForm()

    if login_form.validate_on_submit():
            usuario,funcion=admin_datos.cargar_usuario(nombre_usuario = login_form.nombre_usuario.data,
                                                       contraseña = login_form.contraseña.data)
            
            if funcion in ['inicio_Usuarios_Finales','inicio_jefes']:
                login_user(usuario)
                session['username']=usuario.nombre_usuario
                return redirect(url_for('home'))

            else:
                flash(funcion)
                return render_template("login.html", form=login_form)
            
    else:
        return render_template("login.html", form=login_form)
          
@app.route("/logout", methods=['GET','POST'])
def cerrar_sesion():
    logout_user()
    return redirect(url_for('home'))




##################################################################




@app.route('/analitica')
def analitica():
    departamento = 'maestranza'

    graficador_diagrama=GraficadorDiagramaCircular()
    graficador_nube=GraficadorPalabrasClave()

   # graficador_diagrama.graficar(admin_datos, departamento, 'default', 'svg')
    graficador_nube.graficar(admin_datos, departamento, 'default', 'png')

    return render_template('ANALITICA.html')


if __name__ == "__main__":
    app.run(debug=True)


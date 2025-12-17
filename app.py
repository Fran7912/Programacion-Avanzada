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
        global graficador_diagrama
        global graficador_nube
        
        graficador_diagrama=GraficadorDiagramaCircular()
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

@app.route("/")
def home(): 
    """Acá se inicia el programa"""
    if isinstance(current_user,UsuarioFinal):
        return render_template("InicioUsuarioFinal.html", usuario=current_user.nombre_usuario)
    elif isinstance(current_user,JefeDeDepartamento):
        return render_template ('InicioJefes.html')
    else:
        return render_template('INICIO.html')


@app.route("/register", methods = ['GET','POST'])
def register():

    register_form=RegisterForm()
    
    if register_form.validate_on_submit():
        info = admin_datos.guardar_usuario(email = register_form.email.data, 
                                           nombre_usuario = register_form.nombre_usuario.data, 
                                           contraseña = register_form.contraseña.data, 
                                           nombre = register_form.nombre.data, 
                                           apellido = register_form.apellido.data, 
                                           claustro = register_form.claustro.data )
        
        if info=="usuario guardado exitosamente":
            return redirect(url_for("login"))
        else:
            print(info)
            flash(info)
            return render_template("register.html",form=register_form)
    else:
        return render_template("register.html",form=register_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
   
    login_form=LoginForm()

    if login_form.validate_on_submit():
            usuario,funcion=admin_datos.cargar_usuario(nombre_usuario = login_form.nombre_usuario.data,
                                                       contraseña = login_form.contraseña.data)            
            if funcion in ['inicio_para_usuario_final','inicio_jefes']:
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




#Para usuarios finales


@app.route("/InicioUsuarioFinal", methods=['GET','POST'])
@solo_usuarios_finales
def inicio_Usuarios_Finales():
    return render_template("InicioUsuarioFinal.html", usuario=current_user.nombre_usuario)

@app.route("/crear_reclamo", methods=['GET','POST'])
@solo_usuarios_finales
def formulario_reclamo():
    
    #Cargar imagen si se ingresara
    form_reclamo = FormularioCrearReclamo()
    
    if form_reclamo.validate_on_submit():
            admin_datos.guardar_datos_reclamo(autor=current_user.nombre_usuario, 
                                              titulo=form_reclamo.titulo.data, 
                                              descripcion=form_reclamo.descripcion.data, 
                                              imagen=form_reclamo.imagen.data)
            
            return redirect(url_for('mostrar_reclamos_similares'))
    
    return render_template('crear_reclamo.html', form = form_reclamo)

@app.route("/seleccionar_reclamo_existente")
@solo_usuarios_finales
def mostrar_reclamos_similares():
    
    reclamos=admin_datos.buscar_similares()

    return render_template('reclamos_similares.html', reclamos=reclamos)


@app.route("/confirmar_reclamo")
@solo_usuarios_finales
def crear_reclamo():

    admin_datos.crear_reclamo()
    flash("Reclamo creado con éxito")
    
    return redirect(url_for('home'))


@app.route("/reclamos", methods=['GET','POST'])
@solo_usuarios_finales
def mostrar_reclamos():
    return render_template('reclamos_usuario.html', reclamos=Reclamo.query.all(), usuario=current_user)


@app.route("/mis_reclamos", methods=['GET','POST'])
@solo_usuarios_finales
def mis_reclamos():
    return render_template('reclamos_usuario.html', reclamos=current_user.reclamos_adheridos, usuario=current_user)


@app.route("/adherir/<id>", methods=["GET"])
@solo_usuarios_finales
def adherir_a_reclamo(id):

    admin_datos.adherir_usuario(current_user, id)
    return redirect(url_for("mis_reclamos"))


#Solo JefesDepartamentos

@app.route("/InicioJefe")
@solo_jefes
def inicio_jefes():
    return render_template('InicioJefes.html')

@app.route("/analytics")
@solo_jefes
def analitica():

    departamento = current_user.departamento
    graficador_diagrama.graficar(admin_datos, departamento, 'default', 'svg')
    graficador_nube.graficar(admin_datos, departamento, 'default', 'png')

    return render_template('analitica.html', departamento=departamento.lower().replace(' ', '_'))      

@app.route('/managecomplains')
@solo_jefes
def manejar_reclamos():
    if current_user.departamento=="secretaría técnica":
        reclamos=Reclamo.query.all()
        if len(reclamos)==0:
            flash("No tiene reclamos")
        return render_template("manejar_reclamos.html", reclamos=reclamos)
    else:
        reclamos=Reclamo.query.filter(Reclamo.__table__.c.departamento == current_user.departamento).all()
    if len(reclamos)==0:
            flash("No tiene reclamos")
    return render_template("manejar_reclamos.html", reclamos=reclamos)

@app.route('/help')
@solo_jefes
def ayuda():
    return render_template("ayuda.html")

@app.route("/editar/<id>", methods=["GET","POST"])
@solo_jefes
def editar(id):
    reclamo=Reclamo.query.get(id)

    if current_user.departamento=="secretaría técnica":

        form_editar=ParaSecretarioTecnico()
        if form_editar.validate_on_submit():

            reclamo.estado = form_editar.estado.data
            reclamo.departamento = form_editar.departamento.data
            db.session.commit()
            flash("reclamo editado con éxito")
            return redirect(url_for("manejar_reclamos"))
        
        return render_template("editar_reclamo.html", form=form_editar, reclamo=reclamo)
    
    else:
        form_editar=FormularioEditarReclamo()

        if form_editar.validate_on_submit():
            
            reclamo.estado = form_editar.estado.data
            db.session.commit()                             #cambiar estado del reclamo
            flash("reclamo editado con éxito")
            return redirect(url_for("manejar_reclamos"))
            
    return render_template("editar_reclamo.html", form=form_editar, reclamo=reclamo)

@app.route("/generar_informe/<formato>")
@solo_jefes
def generar_Informe(formato):
    """Genera y descarga informe en PDF o HTML"""
    try:
        if formato == "pdf":
            informante = InformantePDF(
                graficador_torta=graficador_diagrama, 
                graficador_nube=graficador_nube
            )
            
            resultado = informante.generar_informe(
                departamento=current_user.departamento,
                admin_datos=admin_datos
            )
            
            if resultado:
                return resultado
            else:
                flash('Error al generar PDF', 'danger')
                return redirect(url_for('analitica'))
        elif formato == "html":
            informante = InformanteHTML(
                graficador_torta=graficador_diagrama, 
                graficador_nube=graficador_nube
            )
            
            resultado = informante.generar_informe(
                departamento=current_user.departamento,
                admin_datos=admin_datos
            )
            
            if resultado:
                return resultado
            else:
                flash('Error al generar HTML', 'danger')
                return redirect(url_for('analitica'))
        
        else:
            flash('Formato no soportado', 'warning')
            return redirect(url_for('analitica'))
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('analitica'))

if __name__ == "__main__":
    app.run(debug=True)


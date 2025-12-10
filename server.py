from flask import render_template,Flask
app = Flask(__name__)
# Página de inicio
@app.route('/')
def inicio():
    return render_template('INICIO.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

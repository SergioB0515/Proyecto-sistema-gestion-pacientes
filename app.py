"""
Aplicación Flask para el Sistema de Evoluciones Médicas.
Punto de entrada de la aplicación web.
"""

from flask import Flask
from archivos import cargar_json
from modelos import registro
import os
from flask_mysqldb import MySQL
from config import config

# Configurar la ruta de templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


conexion=MySQL(app)

# Cargar datos al iniciar
reg = cargar_json()
if reg is None:
    reg = registro()

# Hacer reg disponible globalmente en la app
app.reg = reg

# Importar rutas DESPUÉS de crear la app
from web.routes import routes_bp
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()

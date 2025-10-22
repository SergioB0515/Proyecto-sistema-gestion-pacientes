"""
Aplicación Flask para el Sistema de Evoluciones Médicas.
Punto de entrada de la aplicación web con PostgreSQL.
"""

from flask import Flask
from modelos import registro
import os

# Configurar la ruta de templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui_cambiar_en_produccion'

# Cargar datos desde PostgreSQL
try:
    from persistencia_db import cargar_registro_db
    reg = cargar_registro_db()
    print("✅ Datos cargados desde PostgreSQL")
except Exception as e:
    print(f"⚠️ Error al cargar desde PostgreSQL, iniciando vacío: {e}")
    reg = registro()

# Hacer reg disponible globalmente en la app
app.reg = reg

# Importar rutas DESPUÉS de crear la app
from web.routes import routes_bp
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    # En desarrollo
    # app.run(debug=True, port=5000)
    
    # En producción (Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
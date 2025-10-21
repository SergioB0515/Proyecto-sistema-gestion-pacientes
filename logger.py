import logging
from datetime import datetime
import os

# Crear carpeta logs si no existe
if not os.path.exists("logs"):
    os.makedirs("logs")
    
# Configurar el logger
logger = logging.getLogger("SistemaEvolucionesM")
logger.setLevel(logging.DEBUG)

# Crear archivo de log
archivo_log = f"logs/evolucionesmedicas_{datetime.now().strftime('%Y-%m-%d')}.log"

# Handler: dónde guardar (archivo)
handler_archivo = logging.FileHandler(archivo_log, encoding="utf-8")
handler_archivo.setLevel(logging.DEBUG)

# Formato: cómo se ve en el archivo
formato = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler_archivo.setFormatter(formato)

# Agregar handler al logger
logger.addHandler(handler_archivo)
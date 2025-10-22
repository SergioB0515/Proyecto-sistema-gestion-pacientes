"""
Script para crear las tablas en PostgreSQL.
Ejecutar una sola vez.
"""

from modelos_db import crear_tablas

if __name__ == "__main__":
    print("Creando tablas en PostgreSQL...")
    try:
        crear_tablas()
        print("✅ Base de datos configurada correctamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
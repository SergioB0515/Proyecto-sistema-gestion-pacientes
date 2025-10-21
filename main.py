"""
Sistema de Registro de Evoluciones Médicas - Punto de entrada.

Este módulo ejecuta la aplicación principal del sistema.
Importa el menú y mantiene el flujo principal del programa.
"""

from menu import menu, seleccionar_opcion

def main():
    """Función principal que ejecuta el programa."""
    while True:
        menu()
        try:
            opcion = int(input("Seleccione una opción: "))
            if opcion == 9:
                print("Saliendo del sistema...")
                break
            seleccionar_opcion(opcion)
        except ValueError:
            print("Por favor, ingrese un número válido\n")

if __name__ == "__main__":
    main()
from datetime import datetime,timedelta

def pedir_cedula():
    """Pide y valida una cédula de 10 dígitos"""
    while True:
        try:
            cedula = int(input("Ingrese la cédula (10 dígitos sin puntos ni comas): "))
            if len(str(cedula)) != 10:
                print("La cédula debe tener exactamente 10 dígitos")
                continue
            return cedula
        except ValueError:
            print("Ingrese un número válido")
def pedir_fecha():
    """Pide y valida una fecha en formato AAAA/MM/DD"""
    while True:
        try:
            print(f"Fecha actual: {datetime.now().date()}")
            fechap = input("Ingrese la fecha (AAAA/MM/DD): ")
            fecha = datetime.strptime(fechap, "%Y/%m/%d").date()
            delta = datetime.now().date()-fecha
            if delta > timedelta(days=90):
                print("La fecha es muy antigua")
                continue
            if fecha > datetime.now().date():
                print("La fecha no puede ser futura")
                continue
            
            return fecha
        except ValueError:
            print("Formato inválido. Use AAAA/MM/DD")
def pedir_hora():
    """Pide y valida una hora en formato HH:MM (24h)"""
    while True:
        try:
            hora = input("Ingrese la hora (HH:MM en formato 24h): ")
            horap = datetime.strptime(hora, "%H:%M").time()
            return horap
        except ValueError:
            print("Formato inválido. Use HH:MM")
def pedir_contenido():
    """Pide y valida el contenido de una evolución (mínimo 35 caracteres y 3 palabras)"""
    while True:
        contenido = input("Ingrese el contenido de la evolución: ")
        
        if len(contenido) < 35:
            print("El contenido es muy corto. Mínimo 35 caracteres")
            continue
        
        palabras = contenido.split()
        if len(palabras) < 3:
            print("El contenido debe tener al menos 3 palabras")
            continue
        
        return contenido
def pedir_nombre():
    """Pide y valida un nombre (solo letras y espacios)"""
    while True:
        nombre = input("Ingrese el nombre: ").strip()
        if not nombre:
            print("El nombre no puede estar vacío")
            continue
        if not nombre.replace(" ", "").isalpha():
            print("El nombre solo puede contener letras y espacios")
            continue
        return nombre

def pedir_apellido():
    """Pide y valida un apellido (solo letras y espacios)"""
    while True:
        apellido = input("Ingrese el apellido: ").strip()
        if not apellido:
            print("El apellido no puede estar vacío")
            continue
        if not apellido.replace(" ", "").isalpha():
            print("El apellido solo puede contener letras y espacios")
            continue
        return apellido
def validar_nombre(nombre):
    """
    Valida que el nombre solo contenga letras y espacios.
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if not nombre or not nombre.strip():
        return False, "El nombre no puede estar vacío"
    
    if not nombre.replace(" ", "").isalpha():
        return False, "El nombre solo puede contener letras y espacios"
    
    return True, ""
def validar_fecha_evolucion(fecha):
    """
    Valida que la fecha no sea futura ni muy antigua.
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    from datetime import timedelta
    
    if fecha > datetime.now().date():
        return False, "La fecha no puede ser futura"
    
    delta = datetime.now().date() - fecha
    if delta > timedelta(days=90):
        return False, "La fecha es muy antigua (máximo 90 días)"
    
    return True, ""
def validar_contenido_evolucion(contenido):
    """
    Valida que el contenido cumpla requisitos.
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if len(contenido) < 35:
        return False, "El contenido es muy corto (mínimo 35 caracteres)"
    
    palabras = contenido.split()
    if len(palabras) < 3:
        return False, "El contenido debe tener al menos 3 palabras"
    
    return True, ""
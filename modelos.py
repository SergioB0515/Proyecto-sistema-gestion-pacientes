from datetime import datetime, date, time, timedelta

class evolucion:
    """
    Representa una evolución médica de un paciente.
    Attributes:
        fecha (date): Fecha en que se realizó la evolución
        hora (time): Hora en que se realizó
        contenido (str): Descripción de la evolución (mínimo 35 caracteres)
        retraso (dict): Diccionario con {'dias': int, 'horas': int, 'minutos': int}
    """
    def __init__(self,fecha : date,hora: time,contenido : str ):
        """
        Inicializa una nueva evolución.
        Args:
            fecha (date): Fecha de la evolución
            hora (time): Hora de la evolución
            contenido (str): Descripción de la evolución
        Raises:
            ValueError: Si el contenido tiene menos de 35 caracteres
        """
        self.fecha = fecha
        self.hora = hora
        self.contenido = contenido
        self.retraso = self.verificar_retraso()
        
    def verificar_retraso(self):
        """
        Calcula el tiempo transcurrido desde que se realizó la evolución.
        
        Returns:
            dict: Diccionario con 'dias', 'horas' y 'minutos' de retraso.
                  Si no hay retraso, retorna {'dias': 0, 'horas': 0, 'minutos': 0}
        """
        fecha_subida=datetime.combine(self.fecha,self.hora)
        delta = datetime.now()-fecha_subida
        if delta > timedelta(days=1):
            dias = delta.days
            horas = delta.seconds // 3600
            minutos = (delta.seconds % 3600) // 60
            return {"dias": dias, "horas": horas, "minutos": minutos}
        return {"dias": 0, "horas": 0, "minutos": 0}
    
    def es_tarde(self):
        """
        Verifica si la evolución tiene retraso.
        
        Returns:
            bool: True si hay retraso, False si no
        """
        r = self.retraso
        return r["dias"] > 0 or r["horas"] > 0 or r["minutos"] > 0
    def exportar_clase(self):
        """
        Convierte la evolución a diccionario para guardar en JSON.
        
        Returns:
            dict: Diccionario serializable con los datos de la evolución
        """
        return {
            "fecha": self.fecha.isoformat(),     
            "hora": self.hora.strftime("%H:%M:%S"),  
            "contenido": self.contenido,
            "retraso": self.retraso
        }
    @classmethod
    def importar_clase(cls, d):
        """
        Crea una evolución desde un diccionario (carga desde JSON).
        
        Args:
            d (dict): Diccionario con los datos de la evolución
            
        Returns:
            evolucion: Instancia de evolución reconstruida
        """
        fecha = datetime.strptime(d["fecha"], "%Y-%m-%d").date()
        hora = datetime.strptime(d["hora"], "%H:%M:%S").time()
        contenido = d["contenido"]
        ev = cls(fecha, hora, contenido)
        if "retraso" in d:
            ev.retraso = d["retraso"]
        return ev

class paciente:
    """
    Representa un paciente en el sistema de fisioterapia.
    
    Un paciente contiene información personal y todas sus evoluciones
    (sesiones de terapia realizadas).
    
    Attributes:
        cedula (int): Cédula de identidad (10 dígitos)
        nombre (str): Nombre del paciente
        apellido (str): Apellido del paciente
        evoluciones (list): Lista de objetos evolucion del paciente
    """
    def __init__(self, cedula: int,nombre: str, apellido: str ):
        """
        Inicializa un nuevo paciente.
        
        Args:
            cedula (int): Cédula de 10 dígitos
            nombre (str): Nombre del paciente
            apellido (str): Apellido del paciente
        """
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.evoluciones = []
        
    def agregar_evolucion(self,evolucion: evolucion):
        """
        Agrega una nueva evolución al paciente.
        
        Args:
            evolucion (evolucion): Objeto evolución a agregar
            
        Raises:
            ValueError: Si ya existe una evolución en la misma fecha
        """
        for ev in self.evoluciones:
            if ev.fecha==evolucion.fecha:
                raise ValueError("Ya existe una evolucion con esa fecha")
        self.evoluciones.append(evolucion)
    
    def eliminar_evolucion(self, indice_evo : int):
        """
        Elimina una evolución del paciente por índice.
        
        Args:
            indice_evo (int): Índice de la evolución a eliminar
            
        Raises:
            ValueError: Si el índice es inválido
        """
        if indice_evo < 0 or indice_evo>=len(self.evoluciones):
            raise ValueError("Seleccione una evolucion valida ")
        del self.evoluciones[indice_evo]
        
    def exportar_clase(self):
        """
        Convierte el paciente a diccionario para guardar en JSON.
        
        Returns:
            dict: Diccionario con datos del paciente y sus evoluciones
        """
        return {
            "cedula": self.cedula,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "evoluciones": [ev.exportar_clase() for ev in self.evoluciones]
        }
    @classmethod
    def importar_clase(cls, d):
        """
        Crea un paciente desde un diccionario (carga desde JSON).
        
        Args:
            d (dict): Diccionario con datos del paciente
            
        Returns:
            paciente: Instancia de paciente reconstruida
        """
        p = cls(int(d["cedula"]), d["nombre"], d["apellido"])
        for ev_d in d.get("evoluciones",[]):
            p.evoluciones.append(evolucion.importar_clase(ev_d))
        return p
class registro:
    """
    Administra todos los pacientes y strikes del sistema.
    
    Es el contenedor principal que gestiona la información global:
    pacientes registrados, evoluciones, y sistema de strikes para
    control de calidad.
    
    Attributes:
        pacientes (dict): Diccionario de pacientes {cedula: paciente}
        strikes (list): Lista de strikes registrados
        total_strikes (int): Contador total de strikes
    """
    def __init__(self):
        """Inicializa un registro vacío."""
        self.pacientes={}     
        self.strikes = []    
        self.total_strikes = 0
    def agregar_paciente(self, paciente: paciente):
        """
        Agrega un nuevo paciente al registro.
        
        Args:
            paciente (paciente): Objeto paciente a agregar
            
        Raises:
            ValueError: Si el paciente ya está registrado
        """
        if paciente.cedula in self.pacientes:
            raise ValueError("Paciente ya registrado.")
        self.pacientes[paciente.cedula] = paciente
    def obtener_paciente(self, cedula: int):
        """
        Obtiene un paciente por su cédula.
        
        Args:
            cedula (int): Cédula del paciente
            
        Returns:
            paciente: Objeto paciente si existe, None si no
        """
        return self.pacientes.get(cedula)

    def asegurar_paciente(self, cedula: int, nombre: str, apellido: str):
        """
    Obtiene un paciente existente o lo crea si no existe.
    Args:
        cedula (int): Cédula del paciente
        nombre (str): Nombre (solo usado si lo crea)
        apellido (str): Apellido (solo usado si lo crea)
        
    Returns:
        paciente: Objeto paciente existente o recién creado
        """
        p = self.obtener_paciente(cedula)
        if p is None:
            p = paciente(cedula, nombre, apellido)
            self.pacientes[cedula] = p
        return p

    def eliminar_paciente(self, cedula: int):
        """
        Elimina un paciente del registro.
        
        Args:
            cedula (int): Cédula del paciente a eliminar
            
        Raises:
            KeyError: Si el paciente no existe
        """
        if cedula in self.pacientes:
            del self.pacientes[cedula]
        else:
            raise KeyError("Paciente no encontrado.")

    def total_evoluciones(self):
        """
        Cuenta el total de evoluciones en el sistema.
        
        Returns:
            int: Número total de evoluciones de todos los pacientes
        """
        return sum(len(p.evoluciones) for p in self.pacientes.values())

    def exportar_clase(self):
        """
        Convierte el registro completo a diccionario para JSON.
        
        Returns:
            dict: Diccionario con pacientes, strikes y total_strikes
        """
        return {
                "pacientes": [p.exportar_clase() for p in self.pacientes.values()],
                "total_strikes": self.total_strikes,
                "strikes": self.strikes
        }

    @classmethod
    def importar_clase(cls, d):
        """
        Crea un registro desde un diccionario (carga desde JSON).
        
        Args:
            d (dict): Diccionario con datos del registro
            
        Returns:
            registro: Instancia de registro reconstruida
        """
        r = cls()
        for p_d in d.get("pacientes", []):
            p = paciente.importar_clase(p_d)
            r.pacientes[p.cedula] = p
        r.strikes = d.get("strikes", [])
        r.total_strikes = d.get("total_strikes", 0)
        return r            
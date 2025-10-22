"""
Funciones para trabajar con PostgreSQL.
CRUD usando SQLAlchemy.
"""

from modelos_db import PacienteDB, EvolucionDB, StrikeDB, obtener_sesion
from modelos import paciente, evolucion, registro
from datetime import datetime

def guardar_registro_db(reg: registro):
    """
    Guarda todo el registro en PostgreSQL.
    Elimina datos anteriores y guarda los nuevos.
    """
    session = obtener_sesion()
    
    try:
        # Limpiar tablas
        session.query(StrikeDB).delete()
        session.query(EvolucionDB).delete()
        session.query(PacienteDB).delete()
        
        # Guardar pacientes
        for p in reg.pacientes.values():
            paciente_db = PacienteDB(
                cedula=p.cedula,
                nombre=p.nombre,
                apellido=p.apellido
            )
            session.add(paciente_db)
            
            # Guardar evoluciones del paciente
            for ev in p.evoluciones:
                evolucion_db = EvolucionDB(
                    cedula_paciente=p.cedula,
                    fecha=ev.fecha,
                    hora=ev.hora,
                    contenido=ev.contenido,
                    retraso=ev.retraso
                )
                session.add(evolucion_db)
        
        # Guardar strikes
        for strike in reg.strikes:
            strike_db = StrikeDB(
                razon=strike['razon'],
                fecha=strike['fecha']
            )
            session.add(strike_db)
        
        session.commit()
        print("✅ Datos guardados en PostgreSQL")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error al guardar: {e}")
        raise
    finally:
        session.close()

def cargar_registro_db():
    """
    Carga todo el registro desde PostgreSQL.
    Reconstruye objetos Python desde la BD.
    """
    session = obtener_sesion()
    
    try:
        reg = registro()
        
        # Cargar pacientes
        pacientes_db = session.query(PacienteDB).all()
        
        for p_db in pacientes_db:
            p = paciente(p_db.cedula, p_db.nombre, p_db.apellido)
            
            # Cargar evoluciones del paciente
            evoluciones_db = session.query(EvolucionDB).filter_by(cedula_paciente=p_db.cedula).all()
            
            for ev_db in evoluciones_db:
                ev = evolucion(ev_db.fecha, ev_db.hora, ev_db.contenido)
                ev.retraso = ev_db.retraso
                p.evoluciones.append(ev)
            
            reg.pacientes[p.cedula] = p
        
        # Cargar strikes
        strikes_db = session.query(StrikeDB).all()
        for strike_db in strikes_db:
            reg.strikes.append({
                "razon": strike_db.razon,
                "fecha": strike_db.fecha
            })
        
        reg.total_strikes = len(reg.strikes)
        
        print("✅ Datos cargados desde PostgreSQL")
        return reg
        
    except Exception as e:
        print(f"❌ Error al cargar: {e}")
        return registro()  # Retorna registro vacío si falla
    finally:
        session.close()
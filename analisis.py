import pandas as pd
from difflib import SequenceMatcher
from modelos import registro
from datetime import datetime
from archivos import exportar_a_excel
    

def obtener_evoluciones_en_tabla(registro_obj: registro, cedula: int):
    """
    Retorna las evoluciones de un paciente en formato DataFrame.
    
    Args:
        registro_obj: Objeto registro del sistema
        cedula: Cédula del paciente
        
    Returns:
        pd.DataFrame con columnas formateadas correctamente
    """
    paciente = registro_obj.obtener_paciente(cedula)
    if paciente is None:
        return None
    
    datos = []
    for ev in paciente.evoluciones:
        datos.append({
            "Fecha": ev.fecha,
            "Hora": ev.hora,
            "Contenido": ev.contenido[:50] + "..." if len(ev.contenido) > 50 else ev.contenido,
            "Retraso (días)": ev.retraso["dias"],
            "Retraso (horas)": ev.retraso["horas"],
            "Retraso (minutos)": ev.retraso["minutos"]
        })
    
    df = pd.DataFrame(datos)
    return df
def obtener_estadisticas_generales(registro_obj: registro):
    """
    Retorna estadísticas generales del sistema.
    
    Returns:
        dict con: total_pacientes, total_evoluciones, total_strikes, promedio_retraso
    """
    total_pacientes = len(registro_obj.pacientes)
    total_strikes = len(registro_obj.strikes)
    total_evoluciones = registro_obj.total_evoluciones()
    
    total_dias = 0
    total_horas = 0
    total_minutos = 0
    
    for paciente in registro_obj.pacientes.values():
        for evolucion in paciente.evoluciones:
            total_dias += evolucion.retraso["dias"]
            total_horas += evolucion.retraso["horas"]
            total_minutos += evolucion.retraso["minutos"]
    
    if total_evoluciones > 0:
        promedio_dias = round(total_dias / total_evoluciones, 2)
        promedio_horas = round(total_horas / total_evoluciones, 2)
        promedio_minutos = round(total_minutos / total_evoluciones, 2)
    else:
        promedio_dias = promedio_horas = promedio_minutos = 0
    
    return {
        "Total Pacientes": total_pacientes,
        "Total Evoluciones": total_evoluciones,
        "Total Strikes": total_strikes,
        "Promedio Retraso (días)": promedio_dias,
        "Promedio Retraso (horas)": promedio_horas,
        "Promedio Retraso (minutos)": promedio_minutos
    }
def obtener_retrasos_por_fecha(registro_obj: registro):
    """
    Retorna un DataFrame con retrasos agrupados por fecha.
    
    Returns:
        pd.DataFrame con columnas: Fecha, Total Retraso (horas)
    """
    datos = []
    for paciente in registro_obj.pacientes.values():
        for ev in paciente.evoluciones:
            retraso_total_horas = ev.retraso["dias"] * 24 + ev.retraso["horas"]
            datos.append({
                "Fecha": ev.fecha,
                "Retraso Total (horas)": retraso_total_horas
            })
    
    if not datos:
        return pd.DataFrame()
    
    df = pd.DataFrame(datos)
    return df.groupby("Fecha")["Retraso Total (horas)"].sum().reset_index()
def obtener_pacientes_con_mas_strikes(registro_obj: registro):
    """
    Retorna un DataFrame con pacientes ordenados por cantidad de strikes.
    
    Returns:
        pd.DataFrame con columnas: Cédula, Nombre, Apellido, Total Strikes
    """
    datos = []
    
    # Contar strikes por paciente (asumir que en strikes hay referencia al paciente)
    # Por ahora, vamos a mostrar estadísticas generales
    for paciente in registro_obj.pacientes.values():
        datos.append({
            "Cédula": paciente.cedula,
            "Nombre": paciente.nombre,
            "Apellido": paciente.apellido,
            "Total Evoluciones": len(paciente.evoluciones)
        })
    
    if not datos:
        return pd.DataFrame()
    
    df = pd.DataFrame(datos)
    return df.sort_values("Total Evoluciones", ascending=False)
def exportar_todos_reportes(registro_obj: registro):
    """
    Función centralizada para manejar toda la exportación de reportes.
    """
    print("\n=== EXPORTAR REPORTES ===")
    print("1. Estadísticas generales")
    print("2. Evoluciones por paciente")
    print("3. Retrasos por fecha")
    print("4. Pacientes con estadísticas")
    print("5. Similitudes de paciente")
    print("6. Todas las similitudes del sistema")
    print("7. Paciente completo (info + evoluciones)")
    print("8. Todos los reportes")
    print("9. Volver")
    
    try:
        op = int(input("Seleccione una opción: "))
        
        if op == 1:
            stats = obtener_estadisticas_generales(registro_obj)
            df = pd.DataFrame([stats])
            print("\n" + df.to_string(index=False))
        
        elif op == 2:
            from utils import pedir_cedula
            cedula = pedir_cedula()
            df = obtener_evoluciones_en_tabla(registro_obj, cedula)
            if df is not None:
                print("\n" + df.to_string(index=False))
            else:
                print("Paciente no encontrado")
        
        elif op == 3:
            df = obtener_retrasos_por_fecha(registro_obj)
            if not df.empty:
                print("\n" + df.to_string(index=False))
            else:
                print("No hay retrasos registrados")
        
        elif op == 4:
            df = obtener_pacientes_con_mas_strikes(registro_obj)
            if not df.empty:
                print("\n" + df.to_string(index=False))
            else:
                print("No hay pacientes registrados")
        
        elif op == 5:
            from utils import pedir_cedula
            cedula = pedir_cedula()
            similitudes_df = pd.DataFrame(encontrar_similitudes_paciente(registro_obj, cedula, umbral=0.85))
            if not similitudes_df.empty:
                print("\n" + similitudes_df.to_string(index=False))
            else:
                print("No se encontraron similitudes en evoluciones de este paciente")
        
        elif op == 6:
            similitudes_df = obtener_todas_similitudes(registro_obj)
            if not similitudes_df.empty:
                print("\n" + similitudes_df.to_string(index=False))
            else:
                print("No se encontraron similitudes en el sistema")
        
        elif op == 7:
            from utils import pedir_cedula
            cedula = pedir_cedula()
            info_df = obtener_informacion_paciente(registro_obj, cedula)
            if info_df is not None:
                print("\n" + info_df.to_string(index=False))
                evoluciones_df = obtener_evoluciones_en_tabla(registro_obj, cedula)
                if evoluciones_df is not None:
                    print("\nEvoluciones:")
                    print(evoluciones_df.to_string(index=False))
            else:
                print("Paciente no encontrado")
        
        elif op == 8:
            print("\n=== ESTADÍSTICAS GENERALES ===")
            stats = obtener_estadisticas_generales(registro_obj)
            df_stats = pd.DataFrame([stats])
            print(df_stats.to_string(index=False))
            
            print("\n=== RETRASOS POR FECHA ===")
            df_retrasos = obtener_retrasos_por_fecha(registro_obj)
            if not df_retrasos.empty:
                print(df_retrasos.to_string(index=False))
            
            print("\n=== PACIENTES CON ESTADÍSTICAS ===")
            df_pacientes = obtener_pacientes_con_mas_strikes(registro_obj)
            if not df_pacientes.empty:
                print(df_pacientes.to_string(index=False))
            
            print("\n=== SIMILITUDES DEL SISTEMA ===")
            similitudes_df = obtener_todas_similitudes(registro_obj)
            if not similitudes_df.empty:
                print(similitudes_df.to_string(index=False))
        
        elif op == 9:
            return
        else:
            print("Opción inválida")
            
    except ValueError:
        print("Ingrese un número válido")
def obtener_informacion_paciente(registro_obj: registro, cedula: int):
    """
    Retorna información general de un paciente en DataFrame.
    
    Returns:
        pd.DataFrame con datos del paciente
    """
    paciente = registro_obj.obtener_paciente(cedula)
    if paciente is None:
        return None
    
    datos = {
        "Cédula": [paciente.cedula],
        "Nombre": [paciente.nombre],
        "Apellido": [paciente.apellido],
        "Total Evoluciones": [len(paciente.evoluciones)]
    }
    
    return pd.DataFrame(datos)
def exportar_paciente_completo(registro_obj: registro, cedula: int):
    """
    Exporta información completa de un paciente a Excel.
    Incluye datos del paciente y todas sus evoluciones.
    
    Args:
        registro_obj: Objeto registro
        cedula: Cédula del paciente
    """
    from archivos import exportar_a_excel
    
    paciente = registro_obj.obtener_paciente(cedula)
    if paciente is None:
        print("Paciente no encontrado")
        return
    
    # Info del paciente
    info_paciente = obtener_informacion_paciente(registro_obj, cedula)
    
    # Evoluciones
    evoluciones = obtener_evoluciones_en_tabla(registro_obj, cedula)
    
    # Exportar
    exportar_a_excel(info_paciente, f"paciente_{cedula}_info")
    if evoluciones is not None:
        exportar_a_excel(evoluciones, f"paciente_{cedula}_evoluciones")
def calcular_similitud(texto1,texto2):
    """
    Calcula el porcentaje de similitud entre dos textos.
    
    Args:
        texto1 (str): Primer texto
        texto2 (str): Segundo texto
        
    Returns:
        float: Porcentaje de similitud (0-1)
    """
    similitud=SequenceMatcher(None, texto1.lower(),texto2.lower()).ratio()
    return similitud
def encontrar_similitudes_paciente(registro_obj, cedula, umbral=0.80):
    """
    Encuentra evoluciones similares de un paciente.
    
    Args:
        registro_obj: Objeto registro
        cedula: Cédula del paciente
        umbral: Porcentaje mínimo para considerar similares (0-1)
        
    Returns:
        list: Lista de dicts con fecha1, fecha2, similitud%
    """
    paciente=registro_obj.obtener_paciente(cedula)
    
    if paciente is None:
        return[]
    
    similitudes=[]
    evoluciones= paciente.evoluciones
    
    for i in range(len(evoluciones)):
        for j in range(i+1, len(evoluciones)):
            ev1 = evoluciones[i]
            ev2 = evoluciones[j]
    
            similitud= calcular_similitud(ev1.contenido, ev2.contenido)
            
            if similitud >= umbral:
                similitudes.append({
                    "fecha 1": ev1.fecha,
                    "fecha 2": ev2.fecha,
                    "similitud" : round(similitud * 100, 2)
                })
    return similitudes
def verificar_similitud_al_subir(contenido_nuevo, evoluciones_existentes, umbral=0.80):
    """
    Verifica si una evolución nueva es similar a las existentes.
    
    Args:
        contenido_nuevo (str): Contenido de la nueva evolución
        evoluciones_existentes (list): Lista de evoluciones del paciente
        umbral: Porcentaje mínimo (0-1)
        
    Returns:
        tuple: (hay_similitud, porcentaje_max, evolución_similar)
    """
    if not evoluciones_existentes:
        return False,0,None
    similitud_max=0
    ev_similar = None
    for ev in evoluciones_existentes:
        similitud=calcular_similitud(contenido_nuevo, ev.contenido)
        
        if similitud > similitud_max:
            similitud_max = similitud
            ev_similar = ev
    if similitud_max >= umbral:
        return True, round(similitud_max*100,2), ev_similar
    return False, similitud_max*100, None
def obtener_todas_similitudes(registro_obj, umbral=0.80):
    """
    Encuentra TODAS las similitudes en TODOS los pacientes.
    
    Returns:
        pd.DataFrame con similitudes globales del sistema
    """
    todas_similitudes=[]
    
    for p in registro_obj.pacientes.values():
        similitudes=encontrar_similitudes_paciente(registro_obj,p.cedula,umbral)
        for sim in similitudes:
            todas_similitudes.append({
                "Cedula" : p.cedula,
                "Nombre" : p.nombre,
                "Apellido" : p.apellido,
                "Fecha 1" : sim["Fecha 1"],
                "Fecha 2" : sim["Fecha 2"],
                "Similitud %" : sim["Similitud"]
            })
    if not todas_similitudes:
        return pd.DataFrame()
    return pd.DataFrame(todas_similitudes)
def verificar_similitud_global(contenido_nuevo, registro_obj, cedula_paciente, umbral=0.87):
    """
    Verifica similitud con evoluciones de TODOS los pacientes.
    Usa umbral más alto para evitar falsos positivos.
    
    Args:
        contenido_nuevo (str): Contenido de la evolución
        registro_obj: Objeto registro
        cedula_paciente: Cédula del paciente actual (para excluir sus propias evoluciones)
        umbral: Porcentaje muy alto (0.95 = 95%)
        
    Returns:
        tuple: (hay_similitud_global, porcentaje, paciente_similar, evolución_similar)
    """
    similitud_max = 0
    ev_similar = None
    paciente_similar = None
    for paciente in registro_obj.pacientes.values():
        # No comparar con el mismo paciente
        if paciente.cedula == cedula_paciente:
            continue
        
        for ev in paciente.evoluciones:
            similitud = calcular_similitud(contenido_nuevo, ev.contenido)
            
            if similitud > similitud_max:
                similitud_max = similitud
                ev_similar = ev
                paciente_similar = paciente
    
    if similitud_max >= umbral:
        return True, round(similitud_max * 100, 2), paciente_similar, ev_similar
    
    return False, similitud_max * 100, None, None
from modelos import evolucion, paciente, registro
from archivos import guardar_json, cargar_json,exportar_a_excel 
from utils import pedir_cedula, pedir_fecha, pedir_hora, pedir_contenido,pedir_apellido,pedir_nombre
from logger import logger
from analisis import obtener_estadisticas_generales, obtener_evoluciones_en_tabla,verificar_similitud_al_subir,verificar_similitud_global
from analisis import obtener_retrasos_por_fecha, obtener_pacientes_con_mas_strikes, exportar_todos_reportes

reg = registro()

def menu():
    print("\n ----Menu Principal---")
    print("1. Subir evolucion ")
    print("2. Consultar evoluciones ")
    print("3. Modificar evolucion ")
    print("4. Eliminar evolucion")
    print("5. Ver estadisticas")
    print("6. Ver reportes")  
    print("7. Guardar informacion ")
    print("8. Cargar informacion  ")
    print("9. Salir ")
def subir_evolucion():
    logger.info("Usuario iniciando subida de evolución")
    cedula = pedir_cedula()
    logger.info(f"Cedula ingresada {cedula}")
    # Verificar si paciente existe
    p = reg.obtener_paciente(cedula)
    if p is None:
        nombre = pedir_nombre()
        apellido = pedir_apellido()
        p = paciente(cedula, nombre, apellido)
        reg.agregar_paciente(p)
        print(f"Paciente {nombre} {apellido} registrado\n")
        logger.info(f"paciente nuevo agregado {nombre} {apellido}")
    else:
        print(f"Paciente encontrado: {p.nombre} {p.apellido}\n")
        logger.info(f"paciente encontrado (ya existente) {p.nombre} {p.apellido}")
    
    # Pedir datos de la evolución
    fecha = pedir_fecha()
    logger.info(f"fecha ingresada : {fecha} ")
    hora = pedir_hora()
    logger.info(f"hora ingresada : {hora} ")
    contenido = pedir_contenido()
    logger.info(f"contenido ingresado : {contenido} ")
    
    hay_similitud, porcentaje, ev_similar = verificar_similitud_al_subir(
        contenido,
        p.evoluciones,
        umbral=0.80
    )
    if hay_similitud:
        print(f"\n⚠️ Contenido muy similiar detectado")
        print(f"\n Similitud del : {porcentaje}")
        print(f"\n Evoluciuon anterior : {ev_similar.fecha}")
        confirmacion=input("¿Continuar de todas formas? \n 1.Si \n 2.No \n")
        
        if confirmacion != 1:
            logger.info("Usuario canceló evolución por similitud detectada")
            print("Operación cancelada\n")
            return
        
        print("⚠️ Strike agregado por similitud detectada\n")
        reg.total_strikes += 1
        reg.strikes.append({
            "razon": f"Evolución similar ({porcentaje}% con fecha {ev_similar.fecha})",
            "fecha": str(fecha)
        })
        logger.warning(f"Strike agregado por similitud: {porcentaje}%")
    hay_similitud_global, porcentaje_global, paciente_similar, ev_similar_global = verificar_similitud_global(
    contenido,
    reg,
    cedula,
    umbral=0.95
    )

    if hay_similitud_global:
        print(f"\n⚠️ ALERTA CRÍTICA: Evolución muy similar en otro paciente")
        print(f"   Similitud: {porcentaje_global}%")
        print(f"   Paciente: {paciente_similar.nombre} {paciente_similar.apellido}")
        print(f"   Fecha: {ev_similar_global.fecha}")
        confirmacion=input("¿Continuar de todas formas? \n 1.Si \n 2.No \n")
        
        if confirmacion !=1:
            logger.warning(f"Usuario canceló evolución por similitud global detectada")
            print("Operación cancelada\n")
            return
        
        # Si continúa, agregar strike
        print("⚠️ Strike agregado por similitud global detectada\n")
        reg.total_strikes += 1
        reg.strikes.append({
            "razon": f"Similitud crítica con paciente {paciente_similar.nombre} ({porcentaje_global}%)",
            "fecha": str(fecha)
        })
        logger.warning(f"Strike crítico: similitud global {porcentaje_global}%")
    # Crear evolución
    ev = evolucion(fecha, hora, contenido)
    logger.info(f"evolucion creada correctamente")
    # Agregar evolución al paciente
    try:
            p.agregar_evolucion(ev)
            print("Evolución subida correctamente\n")        
            logger.info(f"evolucion subida correctamente ")
    except ValueError as e:
            logger.info(f"La evolucion no pudo ser registrada razon {e} ")
            print(f"Error: {e}\n")
            return
        
    # Verificar retraso y agregar strike si es necesario
    if ev.es_tarde():
        razon = "Evolución subida después de las 24 horas"
        reg.total_strikes += 1
        reg.strikes.append({"razon": razon, "fecha": str(fecha)})
        print(f"⚠️ Strike agregado. Total strikes: {reg.total_strikes}\n")
        logger.info(f"evolucion subida subida con retraso ")
def seleccionar_opcion(opcion):
    if opcion == 1:
        subir_evolucion()
    elif opcion == 2:
        consultar_evolucion()
    elif opcion == 3:
        modificar_evolucion()
    elif opcion == 4:
        eliminar_evolucion()
    elif opcion == 5:
        estadisticas()
    elif opcion == 6:
        ver_reportes()  # ← Nueva función
    elif opcion == 7:
        guardar_informacion()
    elif opcion == 8:
        cargar_informacion()
    else:
        print("Ingrese una opción válida")
def consultar_evolucion():
    logger.info(f"Se inicio una nueva consulta ")
    cedula = pedir_cedula()
    logger.info(f"Cedula de la consulta : {cedula} ")
    p = reg.obtener_paciente(cedula)
    if p is None:
        print("Cédula no encontrada\n")
        logger.info(f"El paciente no fue encontrado ")
        return
    
    print(f"Paciente: {p.nombre} {p.apellido}\n")
    logger.info(f"El paciente fue encontrado paciente : {p.nombre} {p.apellido}")
    if not p.evoluciones:
        print("El paciente no tiene evoluciones registradas\n")
        logger.info(f"El paciente no tiene evoluciones subidas")
        return
    
    print("Evoluciones encontradas:\n")
    logger.info(f"Se obtuvo las evoluciones anexadas al paciente")
    for i, ev in enumerate(p.evoluciones, start=1):
        print(f"Evolución #{i}")
        print(f"  Fecha: {ev.fecha}")
        print(f"  Hora: {ev.hora}")
        print(f"  Contenido: {ev.contenido}")
        
        if ev.es_tarde():
            print(f"  Retraso: {ev.retraso['dias']}d {ev.retraso['horas']}h {ev.retraso['minutos']}m")
        else:
            print(f"  Retraso: Ninguno")
        print()
def eliminar_evolucion():
    logger.info(f"Se inicio un proceso de eliminacion de evolucion")
    cedula = pedir_cedula()
    logger.info(f"Cedula de eliminacion {cedula}")
    
    p = reg.obtener_paciente(cedula)
    if p is None:
        print("Cédula no encontrada\n")
        logger.info(f"El paciente no fue encontrado ")
        return
    
    print(f"Paciente: {p.nombre} {p.apellido}\n")
    logger.info(f"El paciente fue encontrado paciente : {p.nombre} {p.apellido} ")
    
    if not p.evoluciones:
        print("El paciente no tiene evoluciones registradas\n")
        logger.info(f"El paciente no tiene evoluciones subidas")
        return
    
    print("Evoluciones encontradas:\n")
    logger.info(f"Se obtuvo las evoluciones anexadas al paciente")
    for i, ev in enumerate(p.evoluciones, start=1):
        print(f"Evolución #{i}")
        print(f"  Fecha: {ev.fecha}")
        print(f"  Hora: {ev.hora}")
    
    try:
        n = int(input("\nSeleccione el número de la evolución a eliminar (0 para cancelar): "))
        if n == 0:
            print("Operación cancelada\n")
            return
        
        p.eliminar_evolucion(n - 1)
        print("Evolución eliminada correctamente\n")
        logger.info(f"Se elimino la evolucion {n} del paciente")
    except ValueError:
        print("Ingrese un número válido\n")
        logger.info(f"opcion no valida")
def modificar_evolucion():
    from analisis import verificar_similitud_al_subir
    
    logger.info(f"Se inicio un proceso de modificacion de evolucion")
    cedula = pedir_cedula()
    logger.info(f"cedula de modificacion {cedula}")
    p = reg.obtener_paciente(cedula)
    if p is None:
        print("Cédula no encontrada\n")
        logger.info(f"paciente no encontrado")
        return
    
    print(f"Paciente: {p.nombre} {p.apellido}\n")
    logger.info(f"Paciente encontrado {p.nombre} {p.apellido} ")
    if not p.evoluciones:
        print("El paciente no tiene evoluciones registradas\n")
        logger.info(f"El paciente no tiene evoluciones registradas")
        return
    
    print("Evoluciones encontradas:\n")
    logger.info(f"Se obtuvo las evoluciones anexadas al paciente")
    for i, ev in enumerate(p.evoluciones, start=1):
        print(f"Evolución #{i}")
        print(f"  Fecha: {ev.fecha}")
        print(f"  Hora: {ev.hora}")
    
    try:
        n = int(input("\nSeleccione el número de la evolución a modificar: "))
        if n < 1 or n > len(p.evoluciones):
            print("Evolución inválida\n")
            logger.info(f"indice de evolucion no encontrado")
            return
        
        ev = p.evoluciones[n - 1]
        
        print("\nModificando evolución...")
        logger.info(f"Evolucion encontrada")
        fecha = pedir_fecha()
        logger.info(f"Nueva fecha de evolucion {fecha}")
        hora = pedir_hora()
        logger.info(f"Nueva hora de evolucion {hora}")
        contenido = pedir_contenido()
        logger.info(f"Nuevo contenido de evolucion {contenido}")
        
        #Verificar similitud con otras evoluciones (excluyendo la que se modifica)
        otras_evoluciones = [e for e in p.evoluciones if e != ev]
        hay_similitud, porcentaje, ev_similar = verificar_similitud_al_subir(
            contenido,
            otras_evoluciones,
            umbral=0.85
        )
        
        if hay_similitud:
            print(f"\n⚠️ ALERTA: Evolución similar detectada")
            print(f"   Similitud: {porcentaje}%")
            print(f"   Evolución anterior: {ev_similar.fecha}")
            confirmacion=input("¿Continuar de todas formas? \n 1.Si \n 2.No \n")
            
            if confirmacion == 2 :
                logger.info("Usuario canceló modificación por similitud detectada")
                print("Operación cancelada\n")
                return
            
            # Si continúa, agregar strike
            print("⚠️ Strike agregado por similitud detectada\n")
            reg.total_strikes += 1
            reg.strikes.append({
                "razon": f"Evolución modificada - Similar ({porcentaje}% con fecha {ev_similar.fecha})",
                "fecha": str(fecha)
            })
            logger.warning(f"Strike agregado en modificación por similitud: {porcentaje}%")
            hay_similitud_global, porcentaje_global, paciente_similar, ev_similar_global = verificar_similitud_global(
            contenido,
        reg,
        cedula,
        umbral=0.95
        )

        if hay_similitud_global:
            print(f"\n⚠️ ALERTA CRÍTICA: Evolución muy similar en otro paciente")
            print(f"   Similitud: {porcentaje_global}%")
            print(f"   Paciente: {paciente_similar.nombre} {paciente_similar.apellido}")
            print(f"   Fecha: {ev_similar_global.fecha}")
            confirmacion=input("¿Continuar de todas formas? \n 1.Si \n 2.No \n")
            
            if confirmacion !=1:
                logger.warning(f"Usuario canceló evolución por similitud global detectada")
                print("Operación cancelada\n")
                return
            
            # Si continúa, agregar strike
            print("⚠️ Strike agregado por similitud global detectada\n")
            reg.total_strikes += 1
            reg.strikes.append({
                "razon": f"Similitud crítica con paciente {paciente_similar.nombre} ({porcentaje_global}%)",
                "fecha": str(fecha)
            })
            logger.warning(f"Strike crítico: similitud global {porcentaje_global}%")
            
        ev.fecha = fecha
        ev.hora = hora
        ev.contenido = contenido
        ev.retraso = ev.verificar_retraso()
        
        if ev.es_tarde():
            reg.total_strikes += 1
            reg.strikes.append({"razon": "Evolución modificada fuera de tiempo", "fecha": str(fecha)})
            print(f"⚠️ Strike agregado por modificación fuera de tiempo\n")
        
        print("Evolución modificada correctamente\n")
        logger.info(f"Evolucion modificada correctamente")
    except ValueError:
        print("Ingrese un número válido\n")
        logger.info(f"opcion invalida")
def estadisticas():
    logger.info(f"se solicito la visualizacion de estadisticas")
    total_evoluciones = reg.total_evoluciones()
    total_strikes = reg.total_strikes
    
    print(f"\n=== ESTADÍSTICAS ===")
    print(f"Total evoluciones: {total_evoluciones}")
    print(f"Total strikes: {total_strikes}")
    
    if total_strikes >= 3:
        print("⚠️ ALERTA: Se han alcanzado 3 o más strikes")
    elif total_strikes == 2:
        print("⚠️ CUIDADO: Estás a un strike de una llamada de atención")
    
    print("\n1. Detalles de strikes")
    print("2. Volver al menú")
    
    try:
        op = int(input("Seleccione una opción: "))
        if op == 1:
            if not reg.strikes:
                print("No hay strikes registrados\n")
            else:
                print("\nDetalles de strikes:\n")
                for i, s in enumerate(reg.strikes, start=1):
                    print(f"Strike #{i}")
                    print(f"  Razón: {s['razon']}")
                    print(f"  Fecha: {s['fecha']}")
                    print()
    except ValueError:
        print("Ingrese un número válido\n")
        logger.warning("Opcion invalida ingresada")
def guardar_informacion():
    from analisis import exportar_todos_reportes
    from archivos import exportar_sistema_completo_excel
    
    logger.info("Proceso de guardado iniciado")
    print("\n=== GUARDAR INFORMACIÓN ===")
    print("1. Guardar datos (JSON)")
    print("2. Guardar sistema completo (Excel)")
    print("3. Exportar reportes")
    print("4. Volver al menú")
    
    try:
        op = int(input("Seleccione una opción: "))
        
        if op == 1:
            try:
                guardar_json(reg)
                print("Información guardada correctamente\n")
                logger.info("Proceso de guardado finalizado con éxito")
            except Exception as e:
                print(f"Error al guardar: {e}\n")
                logger.info(f"Proceso de guardado fallido razón: {e}")
        
        elif op == 2:
            try:
                exportar_sistema_completo_excel(reg)
                logger.info("Sistema completo exportado a Excel")
            except Exception as e:
                print(f"Error al exportar: {e}\n")
                logger.info(f"Error al exportar: {e}")
        
        elif op == 3:
            exportar_todos_reportes(reg)
            logger.info("Reportes exportados")
        
        elif op == 4:
            return
        else:
            print("Opción inválida")
    except ValueError:
        print("Ingrese un número válido")
def cargar_informacion():
    global reg
    logger.info("Proceso de carga de información iniciado")
    
    print("\n=== CARGAR INFORMACIÓN ===")
    print("1. Cargar desde JSON (datos.json)")
    print("2. Cargar desde Excel (datos.xlsx)")
    print("3. Volver al menú")
    
    try:
        op = int(input("Seleccione una opción: "))
        
        if op == 1:
            try:
                reg = cargar_json()
                logger.info("Información cargada correctamente desde JSON")
            except Exception as e:
                print(f"Error al cargar: {e}\n")
                logger.info(f"Error al cargar JSON: {e}")
        
        elif op == 2:
            from archivos import cargar_desde_excel
            try:
                reg_cargado = cargar_desde_excel()
                if reg_cargado is not None:
                    reg = reg_cargado
                    logger.info("Información cargada correctamente desde Excel")
            except Exception as e:
                print(f"Error al cargar Excel: {e}\n")
                logger.info(f"Error al cargar Excel: {e}")
        
        elif op == 3:
            return
        else:
            print("Opción inválida")
            
    except ValueError:
        print("Ingrese un número válido")
def ver_reportes():
    """Muestra menú de reportes disponibles"""
    logger.info("Usuario accedió a reportes")
    
    while True:
        print("\n=== REPORTES ===")
        print("1. Estadísticas generales")
        print("2. Evoluciones por paciente (tabla)")
        print("3. Retrasos por fecha")
        print("4. Pacientes con más evoluciones")
        print("5. Volver al menú")
        
        try:
            op = int(input("Seleccione una opción: "))
            
            if op == 1:
                stats = obtener_estadisticas_generales(reg)
                print("\n=== ESTADÍSTICAS GENERALES ===")
                for key, value in stats.items():
                    print(f"{key}: {value}")
                logger.info("Reporte general visualizado")
                
            elif op == 2:
                cedula = pedir_cedula()
                df = obtener_evoluciones_en_tabla(reg, cedula)
                if df is None:
                    print("Paciente no encontrado")
                else:
                    print("\n" + df.to_string(index=False))
                
            elif op == 3:
                df = obtener_retrasos_por_fecha(reg)
                if df.empty:
                    print("No hay datos de retrasos")
                else:
                    print("\n" + df.to_string(index=False))
                
            elif op == 4:
                df = obtener_pacientes_con_mas_strikes(reg)
                if df.empty:
                    print("No hay pacientes registrados")
                else:
                    print("\n" + df.to_string(index=False))
                
            elif op == 5:
                logger.info("Usuario salió de reportes")
                return
            else:
                print("Opción inválida")
                
        except ValueError:
            print("Ingrese un número válido")
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask import current_app
from modelos import paciente, evolucion
from datetime import datetime
from utils import validar_fecha_evolucion, validar_contenido_evolucion
from logger import logger



# Crear Blueprint
routes_bp = Blueprint('routes', __name__)



@routes_bp.route('/')
def index():
    """Página principal del sistema."""
    reg = current_app.reg
    logger.info("Usuario accedió a página principal")
    total_pacientes = len(reg.pacientes)
    total_evoluciones = reg.total_evoluciones()
    total_strikes = reg.total_strikes
    
    return render_template('index.html', 
                         pacientes=total_pacientes,
                         evoluciones=total_evoluciones,
                         strikes=total_strikes)

@routes_bp.route('/pacientes')
def listar_pacientes():
    """Lista todos los pacientes."""
    reg = current_app.reg
    logger.info("Usuario consultó lista de pacientes")
    return render_template('pacientes.html', pacientes=reg.pacientes.values())

@routes_bp.route('/paciente/<int:cedula>')
def ver_paciente(cedula):
    """Ver detalles de un paciente."""
    reg = current_app.reg
    p = reg.obtener_paciente(cedula)
    if p is None:
        return "Paciente no encontrado", 404
    
    logger.info(f"Usuario consultó paciente: {cedula}")
    return render_template('paciente_detalle.html', paciente=p)

@routes_bp.route('/api/estadisticas')
def api_estadisticas():
    """API que retorna estadísticas en JSON."""
    from analisis import obtener_estadisticas_generales
    reg = current_app.reg
    stats = obtener_estadisticas_generales(reg)
    return jsonify(stats)
@routes_bp.route('/crear-paciente', methods=['GET', 'POST'])
def crear_paciente():
    """Crear un nuevo paciente"""
    if request.method == 'GET':
        return render_template('crear_paciente.html')
    
    elif request.method == 'POST':
        try:
            from utils import validar_nombre
            
            cedula = int(request.form.get('cedula'))
            nombre = request.form.get('nombre').strip()
            apellido = request.form.get('apellido').strip()
            
            # Validar nombre
            valido, error = validar_nombre(nombre)
            if not valido:
                return render_template('crear_paciente.html', error=error)
            
            # Validar apellido
            valido, error = validar_nombre(apellido)
            if not valido:
                return render_template('crear_paciente.html', error=error)
            
            reg = current_app.reg
            
            p = paciente(cedula, nombre, apellido)
            reg.agregar_paciente(p)
            
            logger.info(f"Paciente creado: {nombre} {apellido}")
            guardar_automatico()
            
            return redirect(url_for('routes.listar_pacientes'))
        
        except ValueError as e:
            logger.error(f"Error al crear paciente: {e}")
            return render_template('crear_paciente.html', error=str(e))
        
@routes_bp.route('/subir-evolucion', methods=['GET', 'POST'])
def subir_evolucion():
    """Subir una evolución"""
    from analisis import verificar_similitud_al_subir, verificar_similitud_global
    from utils import validar_fecha_evolucion, validar_contenido_evolucion
    
    reg = current_app.reg
    
    if request.method == 'GET':
        return render_template('subir_evolucion.html', pacientes=reg.pacientes)
    
    elif request.method == 'POST':
        try:
            cedula = int(request.form.get('cedula'))
            fecha_str = request.form.get('fecha')
            hora_str = request.form.get('hora')
            contenido = request.form.get('contenido')
            
            # Convertir tipos
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M").time()
            
            # Obtener paciente
            p = reg.obtener_paciente(cedula)
            if p is None:
                return render_template('subir_evolucion.html',
                                     pacientes=reg.pacientes,
                                     error="Paciente no encontrado")
            
            # VALIDACIONES (primero validar antes de verificar similitud)
            valido, error = validar_fecha_evolucion(fecha)
            if not valido:
                return render_template('subir_evolucion.html',
                                     pacientes=reg.pacientes,
                                     error=error)
            
            valido, error = validar_contenido_evolucion(contenido)
            if not valido:
                return render_template('subir_evolucion.html',
                                     pacientes=reg.pacientes,
                                     error=error)
            
            # VERIFICAR SIMILITUD LOCAL
            hay_similitud, porcentaje, ev_similar = verificar_similitud_al_subir(
                contenido,
                p.evoluciones,
                umbral=0.85
            )
            
            if hay_similitud:
                reg.total_strikes += 1
                reg.strikes.append({
                    "razon": f"Evolución similar ({porcentaje}% con fecha {ev_similar.fecha})",
                    "fecha": str(fecha)
                })
                logger.warning(f"Strike agregado por similitud local: {porcentaje}%")
            
            # VERIFICAR SIMILITUD GLOBAL
            hay_similitud_global, porcentaje_global, paciente_similar, ev_similar_global = verificar_similitud_global(
                contenido,
                reg,
                cedula,
                umbral=0.95
            )
            
            if hay_similitud_global:
                reg.total_strikes += 1
                reg.strikes.append({
                    "razon": f"Similitud crítica con paciente {paciente_similar.nombre} ({porcentaje_global}%)",
                    "fecha": str(fecha)
                })
                logger.warning(f"Strike crítico: similitud global {porcentaje_global}%")
            
            # CREAR Y GUARDAR EVOLUCIÓN
            ev = evolucion(fecha, hora, contenido)
            p.agregar_evolucion(ev)
            
            # VERIFICAR RETRASO
            if ev.es_tarde():
                reg.total_strikes += 1
                reg.strikes.append({
                    "razon": "Evolución subida después de las 24 horas",
                    "fecha": str(fecha)
                })
                logger.warning("Strike por retraso en evolución")
            
            logger.info(f"Evolución subida para paciente {cedula}")
            guardar_automatico()
            
            return redirect(url_for('routes.ver_paciente', cedula=cedula))
        
        except Exception as e:
            logger.error(f"Error al subir evolución: {e}")
            return render_template('subir_evolucion.html',
                                 pacientes=reg.pacientes,
                                 error=str(e))
@routes_bp.route('/eliminar-evolucion/<int:cedula>/<int:indice>')
def eliminar_evolucion(cedula, indice):
    """Elimina una evolución"""
    reg = current_app.reg
    
    try:
            p = reg.obtener_paciente(cedula)
            if p is None:
                return "Paciente no encontrado", 404
            
            p.eliminar_evolucion(indice)
            
            logger.info(f"Evolución eliminada para paciente {cedula}")
            guardar_automatico()
            return redirect(url_for('routes.ver_paciente', cedula=cedula))

    except Exception as e:
            logger.error(f"Error al eliminar evolución: {e}")
            guardar_automatico()
            return f"Error: {e}", 400

    
@routes_bp.route('/eliminar-paciente/<int:cedula>')
def eliminar_paciente(cedula):
    """Elimina un paciente"""
    reg = current_app.reg
    
    try:
        reg.eliminar_paciente(cedula)
        logger.info(f"Paciente eliminado: {cedula}")
        guardar_automatico()
        return redirect(url_for('routes.listar_pacientes'))
    
    except Exception as e:
        logger.error(f"Error al eliminar paciente: {e}")
        guardar_automatico() 
        return f"Error: {e}", 400
    
def guardar_automatico():
    """Guarda automáticamente en PostgreSQL después de operaciones"""
    from persistencia_db import guardar_registro_db
    try:
        guardar_registro_db(current_app.reg)
        logger.info("Guardado automático en PostgreSQL exitoso")
    except Exception as e:
        logger.error(f"Error en guardado automático PostgreSQL: {e}")
@routes_bp.route('/editar-paciente/<int:cedula>', methods=['GET', 'POST'])
def editar_paciente(cedula):
    """Editar un paciente"""
    from utils import validar_nombre
    reg = current_app.reg
    
    p = reg.obtener_paciente(cedula)
    if p is None:
        return "Paciente no encontrado", 404
    
    if request.method == 'GET':
        return render_template('editar_paciente.html', paciente=p)
    
    elif request.method == 'POST':
        try:
            nombre = request.form.get('nombre').strip()
            apellido = request.form.get('apellido').strip()
            
            # Validar nombre
            valido, error = validar_nombre(nombre)
            if not valido:
                return render_template('editar_paciente.html', paciente=p, error=error)
            
            # Validar apellido
            valido, error = validar_nombre(apellido)
            if not valido:
                return render_template('editar_paciente.html', paciente=p, error=error)
            
            # Actualizar datos
            p.nombre = nombre
            p.apellido = apellido
            
            logger.info(f"Paciente editado: {cedula}")
            guardar_automatico()
            
            return redirect(url_for('routes.listar_pacientes'))
        
        except Exception as e:
            logger.error(f"Error al editar paciente: {e}")
            return render_template('editar_paciente.html', paciente=p, error=str(e))
@routes_bp.route('/editar-evolucion/<int:cedula>/<int:indice>', methods=['GET', 'POST'])
def editar_evolucion(cedula, indice):
    """Editar una evolución"""
    from utils import validar_fecha_evolucion, validar_contenido_evolucion
    from analisis import verificar_similitud_al_subir, verificar_similitud_global
    
    reg = current_app.reg
    
    p = reg.obtener_paciente(cedula)
    if p is None or indice < 0 or indice >= len(p.evoluciones):
        return "No encontrado", 404
    
    ev = p.evoluciones[indice]
    
    if request.method == 'GET':
        return render_template('editar_evolucion.html', 
                             paciente=p, 
                             evolucion=ev, 
                             cedula=cedula, 
                             indice=indice)
    
    elif request.method == 'POST':
        try:
            fecha_str = request.form.get('fecha')
            hora_str = request.form.get('hora')
            contenido = request.form.get('contenido')
            
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M").time()
            
            # Validar fecha
            valido, error = validar_fecha_evolucion(fecha)
            if not valido:
                return render_template('editar_evolucion.html', 
                                     paciente=p, evolucion=ev, 
                                     cedula=cedula, indice=indice, error=error)
            
            # Validar contenido
            valido, error = validar_contenido_evolucion(contenido)
            if not valido:
                return render_template('editar_evolucion.html', 
                                     paciente=p, evolucion=ev, 
                                     cedula=cedula, indice=indice, error=error)
            
            # Verificar similitud con otras evoluciones (excluyendo la actual)
            otras_evoluciones = [e for i, e in enumerate(p.evoluciones) if i != indice]
            hay_similitud, porcentaje, ev_similar = verificar_similitud_al_subir(
                contenido,
                otras_evoluciones,
                umbral=0.85
            )
            
            if hay_similitud:
                reg.total_strikes += 1
                reg.strikes.append({
                    "razon": f"Evolución modificada - Similar ({porcentaje}%)",
                    "fecha": str(fecha)
                })
                logger.warning(f"Strike por modificación similar: {porcentaje}%")
            
            # Actualizar evolución
            ev.fecha = fecha
            ev.hora = hora
            ev.contenido = contenido
            ev.retraso = ev.verificar_retraso()
            
            # Verificar retraso
            if ev.es_tarde():
                reg.total_strikes += 1
                reg.strikes.append({
                    "razon": "Evolución modificada fuera de tiempo",
                    "fecha": str(fecha)
                })
                logger.warning("Strike por modificación fuera de tiempo")
            
            logger.info(f"Evolución editada para paciente {cedula}")
            guardar_automatico()
            
            return redirect(url_for('routes.ver_paciente', cedula=cedula))
        
        except Exception as e:
            logger.error(f"Error al editar evolución: {e}")
            return render_template('editar_evolucion.html', 
                                 paciente=p, evolucion=ev, 
                                 cedula=cedula, indice=indice, error=str(e))
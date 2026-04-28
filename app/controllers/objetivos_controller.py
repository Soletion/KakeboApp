"""
Controlador de Objetivos de Ahorro para la aplicación Kakebo
Gestiona las metas de ahorro de los usuarios
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.objetivo_ahorro import ObjetivoAhorro
from app.extensions import db
from datetime import datetime, date
import logging

# Crear blueprint
objetivos_bp = Blueprint('objetivos', __name__)

# Configurar logger
logger = logging.getLogger(__name__)

@objetivos_bp.route('/')
@login_required
def listado():
    """
    Listado de objetivos de ahorro
    """
    try:
        # Obtener resumen de objetivos
        resumen = ObjetivoAhorro.resumen_objetivos(current_user.id)
        
        return render_template(
            'objetivos/listado.html',
            objetivos_activos=resumen['activos'],
            objetivos_completados=resumen['completados'],
            resumen=resumen
        )
        
    except Exception as e:
        logger.error(f"Error cargando listado de objetivos: {str(e)}")
        flash('objetivos.error.general', 'error')
        
        # Crear resumen vacío para evitar error en la plantilla
        resumen_vacio = {
            'activos': [],
            'completados': [],
            'total_objetivo': 0,
            'total_actual': 0,
            'progreso_global': 0
        }
        
        return render_template(
            'objetivos/listado.html',
            objetivos_activos=[],
            objetivos_completados=[],
            resumen=resumen_vacio
        )

@objetivos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """
    Crear un nuevo objetivo de ahorro
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            cantidad_objetivo = request.form.get('cantidad_objetivo', type=float)
            cantidad_actual = request.form.get('cantidad_actual', 0, type=float)
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_limite = request.form.get('fecha_limite')
            
            # Validaciones
            if not nombre:
                flash('objetivos.error.name_required', 'error')
                return render_template('objetivos/formulario.html')
            
            if not cantidad_objetivo or cantidad_objetivo <= 0:
                flash('objetivos.error.invalid_goal_amount', 'error')
                return render_template('objetivos/formulario.html')
            
            if cantidad_actual < 0:
                flash('objetivos.error.invalid_current_amount', 'error')
                return render_template('objetivos/formulario.html')
            
            if not fecha_inicio:
                fecha_inicio = date.today().isoformat()
            
            # Crear objetivo con estado explícito
            objetivo = ObjetivoAhorro(
                usuario_id=current_user.id,
                nombre=nombre,
                descripcion=descripcion,
                cantidad_objetivo=cantidad_objetivo,
                cantidad_actual=cantidad_actual,
                fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
                fecha_limite=datetime.strptime(fecha_limite, '%Y-%m-%d').date() if fecha_limite else None,
                estado='activo'  # ← NUEVO: establecer estado por defecto
            )
            
            db.session.add(objetivo)
            db.session.commit()
            
            logger.info(f"Objetivo creado: {nombre} - Usuario: {current_user.username}")
            flash('objetivos.success.created', 'success')
            
            return redirect(url_for('objetivos.listado'))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando objetivo: {str(e)}")
            flash('objetivos.error.general', 'error')
    
    # GET: Mostrar formulario
    return render_template(
        'objetivos/formulario.html',
        fecha_actual=date.today().isoformat()
    )

@objetivos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """
    Editar un objetivo existente
    """
    objetivo = ObjetivoAhorro.query.get_or_404(id)
    
    # Verificar propiedad
    if objetivo.usuario_id != current_user.id:
        flash('objetivos.error.not_owner', 'error')
        return redirect(url_for('objetivos.listado'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            cantidad_objetivo = request.form.get('cantidad_objetivo', type=float)
            cantidad_actual = request.form.get('cantidad_actual', type=float)
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_limite = request.form.get('fecha_limite')
            
            # Validaciones
            if not nombre:
                flash('objetivos.error.name_required', 'error')
                return render_template('objetivos/formulario.html', objetivo=objetivo)
            
            if not cantidad_objetivo or cantidad_objetivo <= 0:
                flash('objetivos.error.invalid_goal_amount', 'error')
                return render_template('objetivos/formulario.html', objetivo=objetivo)
            
            if cantidad_actual < 0:
                flash('objetivos.error.invalid_current_amount', 'error')
                return render_template('objetivos/formulario.html', objetivo=objetivo)
            
            # Actualizar objetivo
            objetivo.nombre = nombre
            objetivo.descripcion = descripcion
            objetivo.cantidad_objetivo = cantidad_objetivo
            objetivo.cantidad_actual = cantidad_actual
            objetivo.fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            objetivo.fecha_limite = datetime.strptime(fecha_limite, '%Y-%m-%d').date() if fecha_limite else None
            
            db.session.commit()
            
            logger.info(f"Objetivo actualizado: ID {id} - Usuario: {current_user.username}")
            flash('objetivos.success.updated', 'success')
            return redirect(url_for('objetivos.listado'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando objetivo {id}: {str(e)}")
            flash('objetivos.error.general', 'error')
    
    # GET: Mostrar formulario con datos
    return render_template('objetivos/formulario.html', objetivo=objetivo)

@objetivos_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """
    Eliminar un objetivo
    """
    try:
        objetivo = ObjetivoAhorro.query.get_or_404(id)
        
        # Verificar propiedad
        if objetivo.usuario_id != current_user.id:
            flash('objetivos.error.not_owner', 'error')
            return redirect(url_for('objetivos.listado'))
        
        db.session.delete(objetivo)
        db.session.commit()
        
        logger.info(f"Objetivo eliminado: ID {id} - Usuario: {current_user.username}")
        flash('objetivos.success.deleted', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando objetivo {id}: {str(e)}")
        flash('objetivos.error.general', 'error')
    
    return redirect(url_for('objetivos.listado'))

@objetivos_bp.route('/<int:id>/completar', methods=['POST'])
@login_required
def completar(id):
    """
    Marcar objetivo como completado
    """
    try:
        objetivo = ObjetivoAhorro.query.get_or_404(id)
        
        if objetivo.usuario_id != current_user.id:
            flash('objetivos.error.not_owner', 'error')
            return redirect(url_for('objetivos.listado'))
        
        objetivo.marcar_completado()
        
        logger.info(f"Objetivo completado: {objetivo.nombre} - Usuario: {current_user.username}")
        flash('objetivos.success.completed', 'success')
        
    except Exception as e:
        logger.error(f"Error completando objetivo {id}: {str(e)}")
        flash('objetivos.error.general', 'error')
    
    return redirect(url_for('objetivos.listado'))

@objetivos_bp.route('/<int:id>/actualizar-cantidad', methods=['POST'])
@login_required
def actualizar_cantidad(id):
    """
    Actualizar la cantidad actual de un objetivo
    """
    try:
        objetivo = ObjetivoAhorro.query.get_or_404(id)
        
        if objetivo.usuario_id != current_user.id:
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
        data = request.get_json()
        nueva_cantidad = data.get('cantidad', type=float)
        
        if nueva_cantidad is None or nueva_cantidad < 0:
            return jsonify({'success': False, 'error': 'Cantidad inválida'}), 400
        
        objetivo.actualizar_cantidad(nueva_cantidad)
        
        return jsonify({
            'success': True,
            'data': objetivo.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error actualizando cantidad objetivo {id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@objetivos_bp.route('/api/resumen')
@login_required
def api_resumen():
    """
    API endpoint para obtener resumen de objetivos
    """
    try:
        resumen = ObjetivoAhorro.resumen_objetivos(current_user.id)
        
        # Preparar datos para gráfico
        datos_grafico = {
            'labels': [o.nombre for o in resumen['activos']],
            'data': [o.progreso for o in resumen['activos']]
        }
        
        return jsonify({
            'success': True,
            'data': {
                'activos': [o.to_dict() for o in resumen['activos']],
                'completados': [o.to_dict() for o in resumen['completados']],
                'total_objetivo': resumen['total_objetivo'],
                'total_actual': resumen['total_actual'],
                'progreso_global': resumen['progreso_global'],
                'datos_grafico': datos_grafico
            }
        })
        
    except Exception as e:
        logger.error(f"Error en API resumen objetivos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
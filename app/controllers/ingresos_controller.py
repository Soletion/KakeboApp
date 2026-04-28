"""
Controlador de Ingresos para la aplicación Kakebo
Gestiona operaciones CRUD de ingresos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.ingreso import Ingreso
from app.extensions import db
from datetime import datetime, date
import logging

# Crear blueprint
ingresos_bp = Blueprint('ingresos', __name__)

# Configurar logger
logger = logging.getLogger(__name__)

@ingresos_bp.route('/')
@login_required
def listado():
    """
    Listado de ingresos con filtros
    """
    try:
        # Obtener parámetros de filtro
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 20
        tipo = request.args.get('tipo', 'todos')
        fecha_desde = request.args.get('desde', '')
        fecha_hasta = request.args.get('hasta', '')
        
        # Construir filtros
        filtros = {}
        if tipo != 'todos':
            filtros['es_fijo'] = (tipo == 'fijos')
        if fecha_desde:
            filtros['fecha_desde'] = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        if fecha_hasta:
            filtros['fecha_hasta'] = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        # Obtener ingresos filtrados
        ingresos = Ingreso.buscar(current_user.id, **filtros)
        
        # Paginación manual
        total = len(ingresos)
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        ingresos_pagina = ingresos[inicio:fin]
        
        # Calcular totales
        total_ingresos = sum(float(i.cantidad) for i in ingresos)
        total_fijos = sum(float(i.cantidad) for i in ingresos if i.es_fijo)
        total_variables = sum(float(i.cantidad) for i in ingresos if not i.es_fijo)
        
        return render_template(
            'ingresos/listado.html',
            ingresos=ingresos_pagina,
            total_ingresos=total_ingresos,
            total_fijos=total_fijos,
            total_variables=total_variables,
            total_registros=total,
            pagina=pagina,
            total_paginas=(total + por_pagina - 1) // por_pagina,
            filtros_aplicados={
                'tipo': tipo,
                'desde': fecha_desde,
                'hasta': fecha_hasta
            }
        )
        
    except Exception as e:
        logger.error(f"Error cargando listado de ingresos: {str(e)}")
        flash('ingresos.error.general', 'error')
        return render_template('ingresos/listado.html', ingresos=[])

@ingresos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """
    Crear un nuevo ingreso
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cantidad = request.form.get('cantidad', type=float)
            fecha = request.form.get('fecha')
            descripcion = request.form.get('descripcion', '').strip()
            es_fijo = 'es_fijo' in request.form
            
            # Validaciones
            if not cantidad or cantidad <= 0:
                flash('ingresos.error.invalid_amount', 'error')
                return render_template('ingresos/formulario.html')
            
            if not fecha:
                fecha = date.today().isoformat()
            
            # Crear ingreso
            ingreso = Ingreso(
                usuario_id=current_user.id,
                cantidad=cantidad,
                fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
                descripcion=descripcion,
                es_fijo=es_fijo
            )
            
            db.session.add(ingreso)
            db.session.commit()
            
            logger.info(f"Ingreso creado: {cantidad}€ - Usuario: {current_user.username}")
            flash('ingresos.success.created', 'success')
            
            # Redirigir según acción
            if 'guardar_y_otro' in request.form:
                return redirect(url_for('ingresos.nuevo'))
            else:
                return redirect(url_for('ingresos.listado'))
                
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando ingreso: {str(e)}")
            flash('ingresos.error.general', 'error')
    
    # GET: Mostrar formulario
    return render_template(
        'ingresos/formulario.html',
        fecha_actual=date.today().isoformat()
    )

@ingresos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """
    Editar un ingreso existente
    """
    ingreso = Ingreso.query.get_or_404(id)
    
    # Verificar propiedad
    if ingreso.usuario_id != current_user.id:
        flash('ingresos.error.not_owner', 'error')
        return redirect(url_for('ingresos.listado'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cantidad = request.form.get('cantidad', type=float)
            fecha = request.form.get('fecha')
            descripcion = request.form.get('descripcion', '').strip()
            es_fijo = 'es_fijo' in request.form
            
            # Validaciones
            if not cantidad or cantidad <= 0:
                flash('ingresos.error.invalid_amount', 'error')
                return render_template('ingresos/formulario.html', ingreso=ingreso)
            
            # Actualizar ingreso
            ingreso.cantidad = cantidad
            ingreso.fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            ingreso.descripcion = descripcion
            ingreso.es_fijo = es_fijo
            
            db.session.commit()
            
            logger.info(f"Ingreso actualizado: ID {id} - Usuario: {current_user.username}")
            flash('ingresos.success.updated', 'success')
            return redirect(url_for('ingresos.listado'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando ingreso {id}: {str(e)}")
            flash('ingresos.error.general', 'error')
    
    # GET: Mostrar formulario con datos
    return render_template('ingresos/formulario.html', ingreso=ingreso)

@ingresos_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """
    Eliminar un ingreso
    """
    try:
        ingreso = Ingreso.query.get_or_404(id)
        
        # Verificar propiedad
        if ingreso.usuario_id != current_user.id:
            flash('ingresos.error.not_owner', 'error')
            return redirect(url_for('ingresos.listado'))
        
        db.session.delete(ingreso)
        db.session.commit()
        
        logger.info(f"Ingreso eliminado: ID {id} - Usuario: {current_user.username}")
        flash('ingresos.success.deleted', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando ingreso {id}: {str(e)}")
        flash('ingresos.error.general', 'error')
    
    return redirect(url_for('ingresos.listado'))

@ingresos_bp.route('/api/resumen')
@login_required
def api_resumen():
    """
    API endpoint para obtener resumen de ingresos
    """
    try:
        año = request.args.get('año', type=int)
        mes = request.args.get('mes', type=int)
        
        if not año or not mes:
            hoy = date.today()
            año = hoy.year
            mes = hoy.month
        
        total = Ingreso.total_mes(current_user.id, año, mes)
        fijos = Ingreso.ingresos_fijos_mes(current_user.id, año, mes)
        variables = Ingreso.ingresos_variables_mes(current_user.id, año, mes)
        
        total_fijos = sum(float(i.cantidad) for i in fijos)
        total_variables = sum(float(i.cantidad) for i in variables)
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'fijos': total_fijos,
                'variables': total_variables,
                'num_fijos': len(fijos),
                'num_variables': len(variables)
            }
        })
        
    except Exception as e:
        logger.error(f"Error en API resumen ingresos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
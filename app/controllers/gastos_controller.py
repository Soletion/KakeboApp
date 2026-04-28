"""
Controlador de Gastos para la aplicación Kakebo
Gestiona operaciones CRUD de gastos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.gasto import Gasto
from app.models.categoria import Categoria
from app.extensions import db
from datetime import datetime, date
import logging

# Crear blueprint
gastos_bp = Blueprint('gastos', __name__)

# Configurar logger
logger = logging.getLogger(__name__)

@gastos_bp.route('/')
@login_required
def listado():
    """
    Listado de gastos con filtros y paginación
    """
    try:
        # Obtener parámetros de filtro
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 20
        categoria_id = request.args.get('categoria', type=int)
        fecha_desde = request.args.get('desde', '')
        fecha_hasta = request.args.get('hasta', '')
        
        # Construir filtros
        filtros = {}
        if categoria_id:
            filtros['categoria_id'] = categoria_id
        if fecha_desde:
            filtros['fecha_desde'] = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        if fecha_hasta:
            filtros['fecha_hasta'] = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        # Obtener gastos filtrados
        gastos = Gasto.buscar(current_user.id, **filtros)
        
        # Paginación manual
        total = len(gastos)
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        gastos_pagina = gastos[inicio:fin]
        
        # Obtener categorías para el filtro
        categorias = Categoria.obtener_por_idioma()
        
        # Calcular totales
        total_gastos = sum(float(g.cantidad) for g in gastos)
        
        return render_template(
            'gastos/listado.html',
            gastos=gastos_pagina,
            categorias=categorias,
            total_gastos=total_gastos,
            total_registros=total,
            pagina=pagina,
            total_paginas=(total + por_pagina - 1) // por_pagina,
            filtros_aplicados={
                'categoria': categoria_id,
                'desde': fecha_desde,
                'hasta': fecha_hasta
            }
        )
        
    except Exception as e:
        logger.error(f"Error cargando listado de gastos: {str(e)}")
        flash('gastos.error.general', 'error')
        return render_template('gastos/listado.html', gastos=[])

@gastos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """
    Crear un nuevo gasto
    GET: Muestra formulario
    POST: Procesa la creación
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cantidad = request.form.get('cantidad', type=float)
            categoria_id = request.form.get('categoria', type=int)
            fecha = request.form.get('fecha')
            descripcion = request.form.get('descripcion', '').strip()
            
            # Validaciones
            if not cantidad or cantidad <= 0:
                flash('gastos.error.invalid_amount', 'error')
                return render_template('gastos/formulario.html')
            
            if not categoria_id:
                flash('gastos.error.category_required', 'error')
                return render_template('gastos/formulario.html')
            
            if not fecha:
                fecha = date.today().isoformat()
            
            # Crear gasto
            gasto = Gasto(
                usuario_id=current_user.id,
                cantidad=cantidad,
                categoria_id=categoria_id,
                fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
                descripcion=descripcion
            )
            
            db.session.add(gasto)
            db.session.commit()
            
            logger.info(f"Gasto creado: {cantidad}€ - Usuario: {current_user.username}")
            flash('gastos.success.created', 'success')
            
            # Redirigir según acción
            if 'guardar_y_otro' in request.form:
                return redirect(url_for('gastos.nuevo'))
            else:
                return redirect(url_for('gastos.listado'))
                
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando gasto: {str(e)}")
            flash('gastos.error.general', 'error')
    
    # GET: Mostrar formulario
    categorias = Categoria.obtener_por_idioma()
    return render_template(
        'gastos/formulario.html',
        categorias=categorias,
        fecha_actual=date.today().isoformat()
    )

@gastos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """
    Editar un gasto existente
    """
    gasto = Gasto.query.get_or_404(id)
    
    # Verificar propiedad
    if gasto.usuario_id != current_user.id:
        flash('gastos.error.not_owner', 'error')
        return redirect(url_for('gastos.listado'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cantidad = request.form.get('cantidad', type=float)
            categoria_id = request.form.get('categoria', type=int)
            fecha = request.form.get('fecha')
            descripcion = request.form.get('descripcion', '').strip()
            
            # Validaciones
            if not cantidad or cantidad <= 0:
                flash('gastos.error.invalid_amount', 'error')
                return render_template('gastos/formulario.html', gasto=gasto)
            
            if not categoria_id:
                flash('gastos.error.category_required', 'error')
                return render_template('gastos/formulario.html', gasto=gasto)
            
            # Actualizar gasto
            gasto.cantidad = cantidad
            gasto.categoria_id = categoria_id
            gasto.fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            gasto.descripcion = descripcion
            
            db.session.commit()
            
            logger.info(f"Gasto actualizado: ID {id} - Usuario: {current_user.username}")
            flash('gastos.success.updated', 'success')
            return redirect(url_for('gastos.listado'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando gasto {id}: {str(e)}")
            flash('gastos.error.general', 'error')
    
    # GET: Mostrar formulario con datos
    categorias = Categoria.obtener_por_idioma()
    return render_template(
        'gastos/formulario.html',
        gasto=gasto,
        categorias=categorias
    )

@gastos_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """
    Eliminar un gasto
    """
    try:
        gasto = Gasto.query.get_or_404(id)
        
        # Verificar propiedad
        if gasto.usuario_id != current_user.id:
            flash('gastos.error.not_owner', 'error')
            return redirect(url_for('gastos.listado'))
        
        db.session.delete(gasto)
        db.session.commit()
        
        logger.info(f"Gasto eliminado: ID {id} - Usuario: {current_user.username}")
        flash('gastos.success.deleted', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando gasto {id}: {str(e)}")
        flash('gastos.error.general', 'error')
    
    return redirect(url_for('gastos.listado'))

@gastos_bp.route('/<int:id>/detalle')
@login_required
def detalle(id):
    """
    Ver detalle de un gasto
    """
    gasto = Gasto.query.get_or_404(id)
    
    # Verificar propiedad
    if gasto.usuario_id != current_user.id:
        flash('gastos.error.not_owner', 'error')
        return redirect(url_for('gastos.listado'))
    
    return render_template('gastos/detalle.html', gasto=gasto)

@gastos_bp.route('/api/ultimos')
@login_required
def api_ultimos():
    """
    API endpoint para obtener últimos gastos (AJAX)
    """
    try:
        limite = request.args.get('limite', 5, type=int)
        gastos = Gasto.obtener_ultimos(current_user.id, limite)
        
        # Enriquecer con datos de categoría
        categorias = {c.id: c for c in Categoria.query.all()}
        resultado = []
        
        for gasto in gastos:
            gasto_dict = gasto.to_dict()
            categoria = categorias.get(gasto.categoria_id)
            if categoria:
                gasto_dict['categoria_nombre'] = categoria.nombre_es
                gasto_dict['categoria_icono'] = categoria.icono
                gasto_dict['categoria_color'] = categoria.color
            resultado.append(gasto_dict)
        
        return jsonify({'success': True, 'data': resultado})
        
    except Exception as e:
        logger.error(f"Error en API últimos gastos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@gastos_bp.route('/api/buscar')
@login_required
def api_buscar():
    """
    API endpoint para búsqueda de gastos (AJAX)
    """
    try:
        # Obtener filtros
        filtros = {
            'categoria_id': request.args.get('categoria', type=int),
            'descripcion': request.args.get('q', '')
        }
        
        # Fechas
        if request.args.get('desde'):
            filtros['fecha_desde'] = datetime.strptime(
                request.args['desde'], '%Y-%m-%d'
            ).date()
        if request.args.get('hasta'):
            filtros['fecha_hasta'] = datetime.strptime(
                request.args['hasta'], '%Y-%m-%d'
            ).date()
        
        gastos = Gasto.buscar(current_user.id, **filtros)
        
        return jsonify({
            'success': True,
            'data': [g.to_dict() for g in gastos],
            'total': len(gastos)
        })
        
    except Exception as e:
        logger.error(f"Error en API búsqueda gastos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
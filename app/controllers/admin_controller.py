"""
Controlador de administración para Kakebo
Acceso restringido a usuarios con rol de administrador
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app.models.usuario import Usuario
from app.models.gasto import Gasto
from app.models.ingreso import Ingreso
from app.models.objetivo_ahorro import ObjetivoAhorro
from app.extensions import db
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard_admin():
    """
    Panel de administración
    Muestra estadísticas globales de la aplicación
    """
    try:
        # Estadísticas generales
        total_usuarios = Usuario.query.count()
        usuarios_activos = Usuario.query.filter_by(activo=True).count()
        total_gastos = Gasto.query.count()
        total_ingresos = Ingreso.query.count()
        total_objetivos = ObjetivoAhorro.query.count()
        
        # Usuarios recientes
        usuarios_recientes = Usuario.query.order_by(
            Usuario.fecha_registro.desc()
        ).limit(10).all()
        
        # Estadísticas mensuales globales
        hoy = date.today()
        gastos_mes = Gasto.query.filter(
            db.extract('year', Gasto.fecha) == hoy.year,
            db.extract('month', Gasto.fecha) == hoy.month
        ).with_entities(db.func.sum(Gasto.cantidad)).scalar() or 0
        
        ingresos_mes = Ingreso.query.filter(
            db.extract('year', Ingreso.fecha) == hoy.year,
            db.extract('month', Ingreso.fecha) == hoy.month
        ).with_entities(db.func.sum(Ingreso.cantidad)).scalar() or 0
        
        return render_template(
            'admin/dashboard.html',
            total_usuarios=total_usuarios,
            usuarios_activos=usuarios_activos,
            total_gastos=total_gastos,
            total_ingresos=total_ingresos,
            total_objetivos=total_objetivos,
            usuarios_recientes=usuarios_recientes,
            gastos_mes=float(gastos_mes),
            ingresos_mes=float(ingresos_mes)
        )
        
    except Exception as e:
        logger.error(f"Error en panel admin: {str(e)}")
        flash('admin.error.general', 'error')
        return redirect(url_for('dashboard.index'))

@admin_bp.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    """
    Listado de todos los usuarios del sistema
    """
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 20
        
        usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).paginate(
            page=pagina, per_page=por_pagina, error_out=False
        )
        
        return render_template('admin/usuarios.html', usuarios=usuarios)
        
    except Exception as e:
        logger.error(f"Error listando usuarios: {str(e)}")
        flash('admin.error.general', 'error')
        return redirect(url_for('admin.dashboard_admin'))

@admin_bp.route('/usuario/<int:id>')
@login_required
@admin_required
def ver_usuario(id):
    """
    Ver detalle de un usuario específico
    """
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # Obtener estadísticas del usuario
        gastos_totales = Gasto.query.filter_by(usuario_id=usuario.id).with_entities(
            db.func.sum(Gasto.cantidad)
        ).scalar() or 0
        
        ingresos_totales = Ingreso.query.filter_by(usuario_id=usuario.id).with_entities(
            db.func.sum(Ingreso.cantidad)
        ).scalar() or 0
        
        num_gastos = Gasto.query.filter_by(usuario_id=usuario.id).count()
        num_ingresos = Ingreso.query.filter_by(usuario_id=usuario.id).count()
        
        return render_template(
            'admin/usuario_detalle.html',
            usuario=usuario,
            gastos_totales=float(gastos_totales),
            ingresos_totales=float(ingresos_totales),
            num_gastos=num_gastos,
            num_ingresos=num_ingresos
        )
        
    except Exception as e:
        logger.error(f"Error viendo usuario {id}: {str(e)}")
        flash('admin.error.general', 'error')
        return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/usuario/<int:id>/cambiar-rol', methods=['POST'])
@login_required
@admin_required
def cambiar_rol_usuario(id):
    """
    Cambiar el rol de un usuario
    """
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # No permitir cambiar el propio rol
        if usuario.id == current_user.id:
            flash('admin.error.no_self_role_change', 'error')
            return redirect(url_for('admin.ver_usuario', id=id))
        
        nuevo_rol_id = request.form.get('rol_id', type=int)
        
        if nuevo_rol_id:
            usuario.rol_id = nuevo_rol_id
            db.session.commit()
            logger.info(f"Rol de usuario {usuario.username} cambiado a {usuario.rol.nombre}")
            flash('admin.success.rol_changed', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cambiando rol: {str(e)}")
        flash('admin.error.general', 'error')
    
    return redirect(url_for('admin.ver_usuario', id=id))

@admin_bp.route('/usuario/<int:id>/activar-desactivar', methods=['POST'])
@login_required
@admin_required
def toggle_usuario_activo(id):
    """
    Activar o desactivar un usuario
    """
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # No permitir desactivarse a sí mismo
        if usuario.id == current_user.id:
            flash('admin.error.no_self_deactivate', 'error')
            return redirect(url_for('admin.ver_usuario', id=id))
        
        usuario.activo = not usuario.activo
        db.session.commit()
        
        estado = "activado" if usuario.activo else "desactivado"
        logger.info(f"Usuario {usuario.username} {estado} por administrador")
        flash('admin.success.user_toggled', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cambiando estado: {str(e)}")
        flash('admin.error.general', 'error')
    
    return redirect(url_for('admin.ver_usuario', id=id))

@admin_bp.route('/estadisticas')
@login_required
@admin_required
def estadisticas_globales():
    """
    Estadísticas globales de la aplicación
    """
    try:
        from datetime import timedelta
        
        # Usuarios por mes (últimos 12 meses)
        usuarios_por_mes = []
        for i in range(11, -1, -1):
            fecha = date.today() - timedelta(days=30*i)
            count = Usuario.query.filter(
                db.extract('year', Usuario.fecha_registro) == fecha.year,
                db.extract('month', Usuario.fecha_registro) == fecha.month
            ).count()
            usuarios_por_mes.append({
                'mes': fecha.strftime('%B %Y'),
                'count': count
            })
        
        # NUEVO: Obtener todos los usuarios ordenados por fecha de registro
        usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
        
        return render_template(
            'admin/estadisticas.html',
            usuarios_por_mes=usuarios_por_mes,
            usuarios=usuarios
        )
        
    except Exception as e:
        logger.error(f"Error en estadísticas: {str(e)}")
        flash('admin.error.general', 'error')
        return redirect(url_for('admin.dashboard_admin'))
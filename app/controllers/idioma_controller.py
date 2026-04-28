"""
Controlador de Idioma para la aplicación Kakebo
Gestiona el cambio de idioma y preferencias
"""
from flask import Blueprint, request, session, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.idioma_service import IdiomaService
import logging

# Crear blueprint
idioma_bp = Blueprint('idioma', __name__)

# Configurar logger
logger = logging.getLogger(__name__)

@idioma_bp.route('/cambiar/<idioma>')
def cambiar(idioma):
    """
    Cambia el idioma de la aplicación
    """
    try:
        # Validar idioma
        if idioma not in ['es', 'en']:
            idioma = 'es'
        
        # Guardar en sesión
        session['idioma'] = idioma
        
        # Si usuario está autenticado, guardar preferencia
        if current_user.is_authenticated:
            current_user.cambiar_idioma(idioma)
        
        logger.info(f"Idioma cambiado a: {idioma}")
        
        # Mensaje flash en el nuevo idioma
        flash('idioma.success.changed', 'success')
        
    except Exception as e:
        logger.error(f"Error cambiando idioma: {str(e)}")
        flash('idioma.error.general', 'error')
    
    # Redirigir a la página anterior
    return redirect(request.referrer or url_for('dashboard.index'))

@idioma_bp.route('/actualizar-preferencia', methods=['POST'])
@login_required
def actualizar_preferencia():
    """
    Actualiza la preferencia de idioma del usuario (AJAX)
    """
    try:
        data = request.get_json()
        idioma = data.get('idioma', 'es')
        
        if idioma not in ['es', 'en']:
            return jsonify({'success': False, 'error': 'Idioma no válido'}), 400
        
        # Actualizar sesión y base de datos
        session['idioma'] = idioma
        current_user.cambiar_idioma(idioma)
        
        return jsonify({
            'success': True,
            'message': 'Idioma actualizado correctamente'
        })
        
    except Exception as e:
        logger.error(f"Error actualizando preferencia idioma: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@idioma_bp.route('/detectar')
def detectar():
    """
    Detecta el idioma del navegador y redirige
    """
    try:
        # Obtener idioma preferido del navegador
        idioma = request.accept_languages.best_match(['es', 'en'])
        
        if not idioma:
            idioma = 'es'
        
        # Guardar en sesión
        session['idioma'] = idioma
        
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        logger.error(f"Error detectando idioma: {str(e)}")
        return redirect(url_for('dashboard.index'))
"""
Decoradores personalizados para la aplicación Kakebo
Implementa patrones Decorator para autenticación y validación
"""
from functools import wraps
from flask import flash, redirect, url_for, session, request, jsonify, make_response
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)


def logout_required(f):
    """
    Decorador que requiere que el usuario NO esté autenticado
    Útil para páginas de login/registro
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        from flask import session as flask_session
        
        # Verificar si hay sesión activa
        user_authenticated = current_user.is_authenticated
        has_session = flask_session.get('_user_id') is not None
        
        if user_authenticated or has_session:
            # Forzar limpieza
            try:
                logout_user()
                flask_session.clear()
            except:
                pass
            
            flash('auth.error.already_logged_in', 'info')
            response = make_response(redirect(url_for('dashboard.index')))
            response.set_cookie('session', '', expires=0)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Decorador que requiere un rol específico
    
    Uso:
        @role_required('administrador')
        @role_required('usuario', 'administrador')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('auth.error.login_required', 'error')
                return redirect(url_for('auth.login'))
            
            if current_user.rol and current_user.rol.nombre in roles:
                return f(*args, **kwargs)
            
            flash('error.unauthorized', 'error')
            return redirect(url_for('dashboard.index'))
        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorador que requiere que el usuario sea administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('auth.error.login_required', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.es_administrador:
            flash('error.admin_required', 'error')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_or_propietario(model_class, id_param='id'):
    """
    Decorador que permite acceso a administradores o al propietario del recurso
    
    Uso:
        @admin_or_propietario(Gasto, 'gasto_id')
        def editar_gasto(gasto_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('auth.error.login_required', 'error')
                return redirect(url_for('auth.login'))
            
            # Administradores tienen acceso total
            if current_user.es_administrador:
                return f(*args, **kwargs)
            
            # Usuarios normales solo a sus propios recursos
            resource_id = kwargs.get(id_param)
            if resource_id:
                resource = model_class.query.get(resource_id)
                if resource and hasattr(resource, 'usuario_id'):
                    if resource.usuario_id != current_user.id:
                        flash('error.unauthorized', 'error')
                        return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def ajax_required(f):
    """
    Decorador que requiere que la petición sea AJAX
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Se requiere petición AJAX'}), 400
        return f(*args, **kwargs)
    return decorated_function


def log_audit(f):
    """
    Decorador que registra acciones importantes para auditoría
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ejecutar la función
        result = f(*args, **kwargs)
        
        # Registrar en log
        if current_user.is_authenticated:
            logger.info(f"Acción de auditoría - Usuario: {current_user.username} - "
                       f"Ruta: {request.path} - Método: {request.method}")
        
        return result
    return decorated_function


def rate_limit(limite=5, periodo=60):
    """
    Decorador para limitar la tasa de peticiones
    Implementa rate limiting básico por IP
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            key = f"rate_limit:{ip}:{request.path}"
            
            # Aquí se implementaría la lógica con Redis
            # Por ahora solo pasamos
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_csrf(f):
    """
    Decorador para validar token CSRF en peticiones POST
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('csrf_token')
            session_token = session.get('csrf_token')
            
            if not token or token != session_token:
                logger.warning(f"Intento de CSRF detectado desde IP: {request.remote_addr}")
                flash('security.error.csrf', 'error')
                return redirect(request.referrer or url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def inject_idioma(f):
    """
    Decorador que inyecta la función de traducción en el contexto
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.services.idioma_service import IdiomaService
        idioma_service = IdiomaService()
        
        def t(key, **kwargs_t):
            idioma = session.get('idioma', 'es')
            return idioma_service.traducir(key, idioma, **kwargs_t)
        
        # Inyectar función en kwargs
        kwargs['t'] = t
        return f(*args, **kwargs)
    return decorated_function


def handle_errors(f):
    """
    Decorador para manejo centralizado de errores
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en {f.__name__}: {str(e)}")
            flash('error.general', 'error')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': str(e)}), 500
            
            return redirect(url_for('dashboard.index'))
    return decorated_function
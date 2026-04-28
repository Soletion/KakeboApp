"""
Paquete de utilidades para la aplicación Kakebo
Exporta funciones y clases útiles para toda la aplicación
"""
from app.utils.database import DatabaseManager, get_redis, init_db
from app.utils.decorators import (
    logout_required, role_required, ajax_required,
    log_audit, rate_limit, validate_csrf, handle_errors
)
from app.utils.validadores import (
    validar_email, validar_password, validar_username,
    validar_nombre, validar_cantidad, validar_fecha,
    validar_telefono, validar_dni
)
from app.utils.seguridad import (
    generar_token_seguro, verificar_token_seguro,
    generar_csrf_token, validar_csrf_token,
    es_password_segura, generar_password_aleatorio
)
from app.utils.constantes import (
    AuthConstants, DatabaseConstants, FinancialConstants,
    I18nConstants, ValidationConstants, SecurityConstants
)

__all__ = [
    # Database
    'DatabaseManager',
    'get_redis',
    'init_db',
    
    # Decorators
    'logout_required',
    'role_required',
    'ajax_required',
    'log_audit',
    'rate_limit',
    'validate_csrf',
    'handle_errors',
    
    # Validadores
    'validar_email',
    'validar_password',
    'validar_username',
    'validar_nombre',
    'validar_cantidad',
    'validar_fecha',
    'validar_telefono',
    'validar_dni',
    
    # Seguridad
    'generar_token_seguro',
    'verificar_token_seguro',
    'generar_csrf_token',
    'validar_csrf_token',
    'es_password_segura',
    'generar_password_aleatorio',
    
    # Constantes
    'AuthConstants',
    'DatabaseConstants',
    'FinancialConstants',
    'I18nConstants',
    'ValidationConstants',
    'SecurityConstants'
]

# Versión del paquete
__version__ = '1.0.0'
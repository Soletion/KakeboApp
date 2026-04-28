"""
Constantes globales para la aplicación Kakebo
Centraliza todos los valores constantes utilizados en la aplicación
"""
from datetime import timedelta

# ===== CONSTANTES DE LA APLICACIÓN =====
APP_NAME = "Kakebo"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Aplicación de finanzas personales basada en el método japonés Kakebo"

# ===== CONSTANTES DE AUTENTICACIÓN =====
class AuthConstants:
    """Constantes relacionadas con autenticación"""
    
    # Límites de intentos
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 15
    
    # Longitudes mínimas/máximas
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 50
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 20
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 50
    
    # Tiempos de expiración (en segundos)
    SESSION_LIFETIME = 3600  # 1 hora
    REMEMBER_ME_LIFETIME = 604800  # 1 semana
    PASSWORD_RESET_EXPIRY = 86400  # 24 horas
    
    # Tokens
    CSRF_TOKEN_LENGTH = 32
    RESET_TOKEN_LENGTH = 64

# ===== CONSTANTES DE BASE DE DATOS =====
class DatabaseConstants:
    """Constantes relacionadas con la base de datos"""
    
    # Límites de campos
    MAX_STRING_LENGTH = 255
    MAX_TEXT_LENGTH = 1000
    MAX_DESCRIPTION_LENGTH = 500
    
    # Valores por defecto
    DEFAULT_LANGUAGE = 'es'
    DEFAULT_CURRENCY = 'EUR'
    DEFAULT_DECIMAL_PLACES = 2
    
    # Pool de conexiones
    DB_POOL_SIZE = 10
    DB_POOL_MAX_OVERFLOW = 20
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = 1800  # 30 minutos

# ===== CONSTANTES FINANCIERAS =====
class FinancialConstants:
    """Constantes relacionadas con finanzas"""
    
    # Límites monetarios
    MIN_AMOUNT = 0.01
    MAX_AMOUNT = 9999999.99
    MAX_MONTHLY_INCOME = 999999.99
    MAX_MONTHLY_EXPENSE = 999999.99
    
    # Porcentajes
    MAX_SAVINGS_RATE = 100
    MIN_SAVINGS_RATE = 0
    
    # Categorías por defecto (Kakebo)
    CATEGORIES = {
        'essential': {
            'name_es': 'Gastos esenciales',
            'name_en': 'Essential expenses',
            'icon': 'fa-home',
            'color': '#27ae60'
        },
        'discretionary': {
            'name_es': 'Gastos prescindibles',
            'name_en': 'Discretionary expenses',
            'icon': 'fa-shopping-bag',
            'color': '#f39c12'
        },
        'leisure': {
            'name_es': 'Ocio',
            'name_en': 'Leisure',
            'icon': 'fa-film',
            'color': '#3498db'
        },
        'unexpected': {
            'name_es': 'Imprevistos',
            'name_en': 'Unexpected',
            'icon': 'fa-exclamation-triangle',
            'color': '#e74c3c'
        }
    }

# ===== CONSTANTES DE INTERNACIONALIZACIÓN =====
class I18nConstants:
    """Constantes relacionadas con internacionalización"""
    
    # Idiomas soportados
    SUPPORTED_LANGUAGES = ['es', 'en']
    DEFAULT_LANGUAGE = 'es'
    
    # Nombres de idiomas
    LANGUAGE_NAMES = {
        'es': 'Español',
        'en': 'English'
    }
    
    # Formatos de fecha
    DATE_FORMATS = {
        'es': '%d/%m/%Y',
        'en': '%m/%d/%Y'
    }
    
    # Formatos de moneda
    CURRENCY_FORMATS = {
        'es': '{:,.2f} €',
        'en': '€ {:,.2f}'
    }

# ===== CONSTANTES DE VALIDACIÓN =====
class ValidationConstants:
    """Constantes relacionadas con validación"""
    
    # Expresiones regulares
    REGEX_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    REGEX_USERNAME = r'^[a-zA-Z0-9_]{3,20}$'
    REGEX_PASSWORD = r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
    REGEX_PHONE = r'^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$'
    REGEX_DNI = r'^[0-9]{8}[A-Za-z]$'
    
    # Longitudes
    MIN_PASSWORD = 8
    MAX_PASSWORD = 50
    MIN_USERNAME = 3
    MAX_USERNAME = 20
    MIN_NAME = 2
    MAX_NAME = 100

# ===== CONSTANTES DE PAGINACIÓN =====
class PaginationConstants:
    """Constantes relacionadas con paginación"""
    
    # Elementos por página
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # Rangos de páginas
    PAGES_AROUND_CURRENT = 2
    PAGES_AT_EDGES = 1

# ===== CONSTANTES DE CACHÉ =====
class CacheConstants:
    """Constantes relacionadas con caché"""
    
    # Tiempos de expiración (en segundos)
    DEFAULT_TIMEOUT = 300  # 5 minutos
    STATIC_CACHE_TIMEOUT = 3600  # 1 hora
    DASHBOARD_CACHE_TIMEOUT = 180  # 3 minutos
    GRAPH_CACHE_TIMEOUT = 600  # 10 minutos
    
    # Claves de caché
    CACHE_KEY_PREFIX = 'kakebo:'
    CACHE_KEY_CATEGORIES = 'categories'
    CACHE_KEY_STATS = 'stats:user:{user_id}'

# ===== CONSTANTES DE SEGURIDAD =====
class SecurityConstants:
    """Constantes relacionadas con seguridad"""
    
    # Headers de seguridad
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # Content Security Policy
    CSP_DEFAULT = "default-src 'self'"
    CSP_SCRIPT = "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
    CSP_STYLE = "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
    CSP_FONT = "font-src 'self' https://cdnjs.cloudflare.com"
    
    # Cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# ===== CONSTANTES DE LOGS =====
class LogConstants:
    """Constantes relacionadas con logging"""
    
    # Niveles de log
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    DEFAULT_LOG_LEVEL = 'INFO'
    
    # Formatos
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Rotación de archivos
    MAX_LOG_SIZE = 10485760  # 10 MB
    BACKUP_COUNT = 10

# ===== CONSTANTES DE API =====
class ApiConstants:
    """Constantes relacionadas con la API"""
    
    # Versiones
    API_VERSION = 'v1'
    API_PREFIX = '/api/v1'
    
    # Rate limiting
    RATE_LIMIT_DEFAULT = "100/hour"
    RATE_LIMIT_AUTH = "5/minute"
    
    # Códigos de error
    ERROR_CODES = {
        400: 'BAD_REQUEST',
        401: 'UNAUTHORIZED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        429: 'TOO_MANY_REQUESTS',
        500: 'INTERNAL_ERROR'
    }
"""
Archivo de configuración centralizado para la aplicación Kakebo
Gestiona diferentes entornos (desarrollo, testing, producción)
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Configuración de base de datos
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'kakebo_user')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'kakebo_password')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'kakebo_db')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Configuración de Redis
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_URL = os.environ.get('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')
    
    # Configuración de sesión
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
    
    # Configuración de Bcrypt
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    
    # Rate limiting
    LOGIN_MAX_ATTEMPTS = int(os.environ.get('LOGIN_MAX_ATTEMPTS', 5))
    LOGIN_LOCKOUT_MINUTES = int(os.environ.get('LOGIN_LOCKOUT_MINUTES', 15))
    
    # Configuración de logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/kakebo.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10485760))
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 10))
    
    # Configuración de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@kakebo.com')
    
    # Configuración de la aplicación
    APP_NAME = os.environ.get('APP_NAME', 'Kakebo')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'es')
    TIMEZONE = os.environ.get('TIMEZONE', 'Europe/Madrid')
    
    # URLs
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    STATIC_URL = os.environ.get('STATIC_URL', '/static')
    MEDIA_URL = os.environ.get('MEDIA_URL', '/media')
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', SECRET_KEY)
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # HTTP en desarrollo
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
        
    # Logs más detallados
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # Base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Deshabilitar CSRF en tests
    WTF_CSRF_ENABLED = False
    
    # Redis mockeado
    REDIS_URL = 'redis://localhost:6379/1'
    
    # Logs a consola
    LOG_FILE = None


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # Forzar HTTPS
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Configuración de base de datos para producción
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'max_overflow': 10,
    }
    
    # Logs en producción
    LOG_LEVEL = 'WARNING'
    
    # Cache estática
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 año


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])


# Configuración activa
Config = get_config()
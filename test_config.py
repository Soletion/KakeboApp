# test_config.py (reemplaza TODO el contenido)
"""
Configuración específica para pruebas
"""

class TestConfig:
    """Configuración para entorno de pruebas"""
    TESTING = True
    SECRET_KEY = 'test-secret-key-12345'
    
    # Base de datos en memoria para pruebas (SQLite no necesita pool)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLite no soporta pool_size, así que lo omitimos
    
    # Deshabilitar CSRF para pruebas
    WTF_CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False
    
    # Configuración de sesión
    SERVER_NAME = 'localhost.localdomain'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging
    LOG_LEVEL = 'ERROR'
    
    # Idiomas
    LANGUAGES = ['es', 'en']
    DEFAULT_LANGUAGE = 'es'
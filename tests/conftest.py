# tests/conftest.py
import sys
import os
import pytest

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar configuración de pruebas
from test_config import TestConfig
from app import create_app
from app.extensions import db
from app.models.rol import Rol
from app.models.categoria import Categoria
from app.models.usuario import Usuario

@pytest.fixture(scope='session')
def app():
    """Fixture para la aplicación Flask en modo pruebas"""
    app = create_app(TestConfig)
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Inicializar roles
        Rol.inicializar_roles()
        
        # Inicializar categorías
        from app.utils.database import init_db
        init_db()
    
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Cliente de pruebas HTTP"""
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    """Sesión de base de datos para pruebas"""
    with app.app_context():
        # Iniciar una transacción
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Usar la sesión normal pero ligada a la transacción
        db.session.connection = lambda: connection
        
        yield db.session
        
        # Rollback después de cada prueba
        transaction.rollback()
        connection.close()

@pytest.fixture(scope='function')
def app_context(app):
    """Contexto de aplicación para pruebas"""
    with app.app_context():
        yield

@pytest.fixture(scope='function')
def usuario_normal(session):
    """Crear usuario normal para pruebas"""
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    
    # Verificar si ya existe un rol usuario
    rol_usuario = Rol.query.filter_by(nombre='usuario').first()
    if not rol_usuario:
        rol_usuario = Rol(nombre='usuario', descripcion='Usuario normal')
        session.add(rol_usuario)
        session.commit()
    
    usuario = Usuario(
        username='testuser',
        email='test@example.com',
        nombre='Test',
        apellidos='User',
        password_hash=bcrypt.generate_password_hash('Test123456').decode('utf-8'),
        activo=True,
        idioma_preferido='es',
        rol_id=rol_usuario.id
    )
    session.add(usuario)
    session.commit()
    
    return usuario

@pytest.fixture(scope='function')
def authenticated_client(client, usuario_normal, app):
    """Cliente HTTP autenticado"""
    with app.test_request_context():
        with client.session_transaction() as sess:
            sess['_user_id'] = str(usuario_normal.id)
            sess['_fresh'] = True
    
    return client

@pytest.fixture(scope='function')
def test_client(app):
    """Cliente de pruebas para integración"""
    return app.test_client()

@pytest.fixture(scope='function')
def auth_headers(test_client, usuario_normal):
    """Headers de autenticación para pruebas API"""
    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(usuario_normal.id)
        sess['_fresh'] = True
    return test_client
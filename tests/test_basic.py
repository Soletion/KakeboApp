# Test básico para verificar que la aplicación se configura correctamente y que la base de datos funciona.
import pytest
from flask import current_app
from app.extensions import db
from app.models.rol import Rol
from app.models.usuario import Usuario

def test_app_exists(app):
    """Prueba que la aplicación existe"""
    assert app is not None

def test_app_is_testing(app):
    """Prueba que está en modo testing"""
    assert app.config['TESTING'] == True

def test_database_roles(session):
    """Prueba que los roles existen"""
    roles = Rol.query.all()
    assert len(roles) >= 2

def test_create_user(session):
    """Prueba crear usuario"""
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    
    user = Usuario(
        username='testuser2',
        email='test2@example.com',
        nombre='Test2',
        password_hash=bcrypt.generate_password_hash('Test123456').decode('utf-8'),
        rol_id=1
    )
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.username == 'testuser2'
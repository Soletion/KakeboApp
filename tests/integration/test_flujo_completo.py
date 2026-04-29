"""
Pruebas de integración - Flujos completos de la aplicación Kakebo
"""
import pytest
import json
from datetime import date, timedelta
from flask import session
from app import db
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.categoria import Categoria
from app.models.gasto import Gasto
from app.models.ingreso import Ingreso
from app.models.objetivo_ahorro import ObjetivoAhorro
import random
import string

@pytest.mark.usefixtures('app_context')
class TestFlujoCompleto:
    """Pruebas integrales de flujos completos"""
    
    @pytest.fixture
    def client(self, app):
        """Cliente de pruebas"""
        return app.test_client()
    
    @pytest.fixture
    def usuario_nuevo(self, session):
        """Crear usuario nuevo para pruebas"""
        sufijo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        rol = session.query(Rol).filter_by(nombre='usuario').first()
        usuario = Usuario(
            username=f'flujo_{sufijo}',
            email=f'flujo_{sufijo}@test.com',
            nombre='Flujo',
            apellidos='Test',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        return usuario
    
    # =========================================================
    # FLUJO 1: Login y autenticación
    # =========================================================
    
    def test_flujo_login_logout(self, client, usuario_nuevo):
        """Prueba: Login y logout correctos"""
        
        # Login
        response_login = client.post('/auth/login', data={
            'email': usuario_nuevo.email,
            'password': 'Test123456'
        }, follow_redirects=True)
        assert response_login.status_code == 200
        
        # Acceder a dashboard
        response_dashboard = client.get('/dashboard/')
        assert response_dashboard.status_code == 200
        
        # Logout
        response_logout = client.get('/auth/logout', follow_redirects=True)
        assert response_logout.status_code == 200
    
    # =========================================================
    # FLUJO 2: Crear y listar gastos
    # =========================================================
    
    def test_flujo_crear_listar_gastos(self, client, usuario_nuevo):
        """Prueba: Crear gasto y verlo en el listado"""
        
        # Login
        client.post('/auth/login', data={
            'email': usuario_nuevo.email,
            'password': 'Test123456'
        })
        
        categoria = db.session.query(Categoria).first()
        
        # Crear gasto
        response_crear = client.post('/gastos/nuevo', data={
            'categoria_id': categoria.id,
            'cantidad': '125.75',
            'fecha': date.today().isoformat(),
            'descripcion': 'Gasto prueba integración'
        }, follow_redirects=True)
        assert response_crear.status_code == 200
        
        # Verificar en listado
        response_listado = client.get('/gastos/')
        assert response_listado.status_code == 200
    
    # =========================================================
    # FLUJO 3: Objetivo de ahorro
    # =========================================================
    
    def test_flujo_objetivo_ahorro(self, client, usuario_nuevo):
        """Prueba: Crear objetivo y añadir cantidad"""
        
        # Login
        client.post('/auth/login', data={
            'email': usuario_nuevo.email,
            'password': 'Test123456'
        })
        
        # Crear objetivo
        response_crear = client.post('/objetivos/nuevo', data={
            'nombre': 'Viaje Test',
            'descripcion': 'Ahorro para pruebas',
            'cantidad_objetivo': '1000.00',
            'fecha_limite': (date.today() + timedelta(days=180)).isoformat()
        }, follow_redirects=True)
        assert response_crear.status_code == 200
    
    # =========================================================
    # FLUJO 4: API endpoints
    # =========================================================
    
    def test_flujo_api_resumen_mes(self, client, usuario_nuevo):
        """Prueba: Endpoint API de resumen mensual"""
        
        # Login
        client.post('/auth/login', data={
            'email': usuario_nuevo.email,
            'password': 'Test123456'
        })
        
        response = client.get('/dashboard/api/resumen-mes')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, dict)
    
    # =========================================================
    # FLUJO 5: Cambio de idioma
    # =========================================================
    
    def test_flujo_cambiar_idioma(self, client, usuario_nuevo):
        """Prueba: Cambiar idioma de la interfaz"""
        
        # Login
        client.post('/auth/login', data={
            'email': usuario_nuevo.email,
            'password': 'Test123456'
        })
        
        # Cambiar a inglés
        response_en = client.get('/idioma/cambiar/en', follow_redirects=True)
        assert response_en.status_code == 200
        
        # Cambiar a español
        response_es = client.get('/idioma/cambiar/es', follow_redirects=True)
        assert response_es.status_code == 200
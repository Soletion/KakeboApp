"""
Paquete de fixtures para tests
Datos y configuraciones reutilizables en toda la suite de pruebas
"""
import pytest
from datetime import date, timedelta
import random
import string

# Exportar fixtures principales
from tests.fixtures.datos_prueba import (
    datos_usuarios_prueba,
    datos_gastos_prueba,
    datos_ingresos_prueba,
    datos_objetivos_prueba,
    datos_completos_prueba,
    escenario_mensual_completo,
    escenario_historico
)

@pytest.fixture
def random_string():
    """Genera un string aleatorio de longitud específica"""
    def _random_string(length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return _random_string

@pytest.fixture
def random_email(random_string):
    """Genera un email aleatorio"""
    return f"{random_string(8)}@test.com"

@pytest.fixture
def random_amount():
    """Genera una cantidad monetaria aleatoria"""
    def _random_amount(minimo=10, maximo=1000):
        return round(random.uniform(minimo, maximo), 2)
    return _random_amount

@pytest.fixture
def random_date():
    """Genera una fecha aleatoria en un rango"""
    def _random_date(inicio=date.today() - timedelta(days=365), 
                      fin=date.today()):
        delta = fin - inicio
        random_days = random.randint(0, delta.days)
        return inicio + timedelta(days=random_days)
    return _random_date

@pytest.fixture
def limpiar_base_datos(request, session):
    """Fixture para limpiar tablas específicas después de tests"""
    def _limpiar_tablas(tablas):
        for tabla in tablas:
            session.execute(f"DELETE FROM {tabla}")
        session.commit()
    
    # Registrar función de cleanup
    request.addfinalizer(lambda: _limpiar_tablas([]))
    return _limpiar_tablas

# Configuración de pytest
def pytest_configure(config):
    """Configuración global de marcadores"""
    config.addinivalue_line(
        "markers",
        "fixture: Marca un test que utiliza fixtures específicos"
    )

# Hook para mostrar información de fixtures
@pytest.hookimpl(tryfirst=True)
def pytest_report_header(config):
    """Añade información al header de pytest"""
    return [
        "Kakebo Test Fixtures:",
        f"  - Usuarios de prueba disponibles",
        f"  - Datos financieros de ejemplo",
        f"  - Escenarios preconfigurados"
    ]
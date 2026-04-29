"""
Paquete de tests de integración para Kakebo
Pruebas que verifican la interacción entre múltiples componentes
"""
import pytest

# Marcadores personalizados para tests de integración
def pytest_configure(config):
    """Configura marcadores personalizados"""
    config.addinivalue_line(
        "markers",
        "integration: Marca un test como de integración (flujos completos)"
    )
    config.addinivalue_line(
        "markers",
        "database: Marca un test como prueba de base de datos"
    )
    config.addinivalue_line(
        "markers",
        "api: Marca un test como prueba de API"
    )
    config.addinivalue_line(
        "markers",
        "slow: Marca un test como lento (puede omitirse con -m 'not slow')"
    )

# Configuración específica para tests de integración
@pytest.fixture(scope="session", autouse=True)
def integration_setup():
    """
    Setup global para tests de integración
    Se ejecuta automáticamente antes de todos los tests
    """
    print("\n Inicializando entorno de tests de integración...")
    yield
    print("\n Limpiando entorno de tests de integración...")
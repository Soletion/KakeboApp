"""
Paquete de tests unitarios para utilidades
Pruebas de funciones helper y utilidades
"""
import pytest

# Configuración específica para tests de utils
pytestmark = pytest.mark.utils

# Fixtures compartidas para tests de utils
@pytest.fixture
def datos_prueba_texto():
    """Fixture con datos de texto para pruebas de validación"""
    return {
        'vacio': '',
        'espacios': '   ',
        'normal': 'Texto normal',
        'con_html': '<script>alert("test")</script>',
        'con_sql': "Robert'; DROP TABLE users; --",
        'largo': 'a' * 1000,
        'email_valido': 'test@example.com',
        'email_invalido': 'test@.com'
    }

@pytest.fixture
def datos_prueba_numericos():
    """Fixture con datos numéricos para pruebas"""
    return {
        'entero': 42,
        'decimal': 3.14159,
        'negativo': -10,
        'cero': 0,
        'grande': 10**6,
        'string_numero': '123.45',
        'string_invalido': 'abc'
    }
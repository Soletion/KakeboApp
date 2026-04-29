"""
Paquete de tests unitarios para modelos
Pruebas de modelos de base de datos y sus métodos
"""
import pytest

# Configuración específica para tests de modelos
pytestmark = pytest.mark.model

# Fixtures compartidas para tests de modelos
@pytest.fixture
def datos_modelos():
    """Fixture con datos comunes para pruebas de modelos"""
    from datetime import date, timedelta
    
    return {
        'fecha_hoy': date.today(),
        'fecha_ayer': date.today() - timedelta(days=1),
        'fecha_manana': date.today() + timedelta(days=1),
        'cantidad_valida': 100.50,
        'cantidad_cero': 0,
        'cantidad_negativa': -50.25
    }

@pytest.fixture
def relaciones_esperadas():
    """Fixture con las relaciones esperadas entre modelos"""
    return {
        'Usuario': ['gastos', 'ingresos', 'objetivos'],
        'Gasto': ['usuario', 'categoria_rel'],
        'Ingreso': ['usuario'],
        'ObjetivoAhorro': ['usuario'],
        'Categoria': ['gastos']
    }

def assert_model_valid(model, expected_attrs):
    """
    Función helper para verificar que un modelo tiene los atributos esperados
    """
    for attr in expected_attrs:
        assert hasattr(model, attr), f"Modelo {model.__class__.__name__} no tiene atributo {attr}"
"""
Paquete de tests unitarios para servicios
Pruebas de lógica de negocio en servicios
"""
import pytest

# Configuración específica para tests de servicios
pytestmark = pytest.mark.service

# Fixtures compartidas para tests de servicios
@pytest.fixture
def servicios_disponibles():
    """Fixture con lista de servicios disponibles"""
    return [
        'AuthService',
        'CalculoService',
        'GraficoService',
        'IdiomaService'
    ]

@pytest.fixture
def datos_calculo():
    """Fixture con datos para pruebas de cálculos financieros"""
    return {
        'ingresos': [1000, 1500, 2000],
        'gastos': [500, 700, 300],
        'objetivos': [
            {'nombre': 'Viaje', 'actual': 300, 'objetivo': 1000},
            {'nombre': 'Coche', 'actual': 1500, 'objetivo': 5000}
        ]
    }

@pytest.fixture
def fechas_prueba():
    """Fixture con fechas para pruebas temporales"""
    from datetime import date, timedelta
    
    return {
        'hoy': date.today(),
        'inicio_mes': date.today().replace(day=1),
        'fin_mes': (date.today().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1),
        'enero_2024': date(2024, 1, 15)
    }

def assert_service_method(service, method_name, args=None):
    """
    Función helper para verificar que un servicio tiene un método
    """
    assert hasattr(service, method_name), f"Servicio {service.__class__.__name__} no tiene método {method_name}"
    if args:
        method = getattr(service, method_name)
        assert callable(method), f"{method_name} no es un método invocable"
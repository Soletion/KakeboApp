"""
Paquete de tests unitarios para Kakebo
Contiene pruebas aisladas de componentes individuales
"""
import pytest

# Marcadores personalizados para tests unitarios
def pytest_configure(config):
    """Configura marcadores personalizados"""
    config.addinivalue_line(
        "markers",
        "unit: Marca un test como unitario (prueba aislada de un componente)"
    )
    config.addinivalue_line(
        "markers",
        "model: Marca un test como prueba de modelo"
    )
    config.addinivalue_line(
        "markers",
        "service: Marca un test como prueba de servicio"
    )
    config.addinivalue_line(
        "markers",
        "utils: Marca un test como prueba de utilidad"
    )

# Hook para saltar tests de integración en esta suite
def pytest_collection_modifyitems(config, items):
    """Modifica la colección de tests para excluir los de integración"""
    if config.getoption("-m") != "integration":
        items[:] = [item for item in items if "integration" not in item.keywords]
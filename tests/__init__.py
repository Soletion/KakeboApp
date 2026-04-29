"""
Paquete de tests para la aplicación Kakebo
Configuración global y punto de entrada para la suite de pruebas
"""
import pytest
import os
import sys

# Añadir el directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuración global de pytest
pytest_plugins = [
    'tests.fixtures.datos_prueba',
]

def run_tests():
    """
    Función para ejecutar todos los tests desde línea de comandos
    Uso: python -m tests
    """
    pytest.main(["-v", "--cov=app", "--cov-report=html", "tests/"])
    
if __name__ == '__main__':
    run_tests()
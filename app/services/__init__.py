"""
Inicializador del paquete services
Exporta todos los servicios para facilitar importaciones
"""
from app.services.auth_service import AuthService
from app.services.calculo_service import CalculoService
from app.services.grafico_service import GraficoService
from app.services.idioma_service import IdiomaService

# Lista de servicios disponibles
__all__ = [
    'AuthService',
    'CalculoService',
    'GraficoService',
    'IdiomaService'
]

# Instancias singleton de servicios (opcional)
auth_service = AuthService()
calculo_service = CalculoService()
grafico_service = GraficoService()
idioma_service = IdiomaService()
"""
Inicializador del paquete models
Exporta todos los modelos para facilitar importaciones
"""
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.gasto import Gasto
from app.models.ingreso import Ingreso
from app.models.objetivo_ahorro import ObjetivoAhorro

# Lista de modelos para facilitar importaciones
__all__ = [
    'Usuario', 
    'Categoria', 
    'Gasto', 
    'Ingreso', 
    'ObjetivoAhorro'
]
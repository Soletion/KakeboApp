"""
Utilidades de Base de Datos para la aplicación Kakebo
Implementa patrón Singleton para la conexión y utilidades de BD
"""
from app.extensions import db
from app.models.categoria import Categoria
from flask import current_app
import logging
import pymysql
import redis

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestor de base de datos con patrón Singleton
    Centraliza operaciones de base de datos
    """
    
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_inicializado'):
            self._inicializado = True
            self._init_pool()
    
    def _init_pool(self):
        """Inicializa el pool de conexiones"""
        try:
            config = current_app.config
            self._connection_pool = pymysql.connect(
                host=config.get('MYSQL_HOST', 'localhost'),
                user=config.get('MYSQL_USER'),
                password=config.get('MYSQL_PASSWORD'),
                database=config.get('MYSQL_DB'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("Pool de conexiones MySQL inicializado")
        except Exception as e:
            logger.error(f"Error inicializando pool de conexiones: {e}")
    
    def get_connection(self):
        """Obtiene una conexión del pool"""
        return self._connection_pool

def get_redis():
    """Obtiene una conexión Redis para caché y rate limiting"""
    try:
        # Temporalmente deshabilitado hasta instalar Redis
        # redis_client = redis.Redis(
        #     host=current_app.config.get('REDIS_HOST', 'localhost'),
        #     port=current_app.config.get('REDIS_PORT', 6379),
        #     db=current_app.config.get('REDIS_DB', 0),
        #     decode_responses=True
        # )
        # redis_client.ping()
        # return redis_client
        return None  #  Temporal: Redis no configurado
    except Exception as e:
        logger.warning(f"No se pudo conectar a Redis: {e}")
        return None

def init_db():
    """
    Inicializa la base de datos con datos por defecto
    """
    try:
        # Crear tablas
        db.create_all()
        
        # Inicializar categorías
        Categoria.inicializar_categorias()
        
        # Crear índices recomendados
        crear_indices()
        
        logger.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")

def crear_indices():
    """
    Crea índices optimizados para las consultas más frecuentes
    """
    try:
        # Índices para tabla de gastos
        db.session.execute(
            "CREATE INDEX IF NOT EXISTS idx_gastos_usuario_fecha "
            "ON gastos(usuario_id, fecha)"
        )
        
        db.session.execute(
            "CREATE INDEX IF NOT EXISTS idx_gastos_categoria "
            "ON gastos(categoria_id)"
        )
        
        # Índices para tabla de ingresos
        db.session.execute(
            "CREATE INDEX IF NOT EXISTS idx_ingresos_usuario_fecha "
            "ON ingresos(usuario_id, fecha)"
        )
        
        # Índices para tabla de objetivos
        db.session.execute(
            "CREATE INDEX IF NOT EXISTS idx_objetivos_usuario_estado "
            "ON objetivos_ahorro(usuario_id, estado)"
        )
        
        db.session.commit()
        logger.info("Índices de base de datos creados")
        
    except Exception as e:
        logger.warning(f"Error creando índices: {e}")

def ejecutar_consulta(sql, params=None):
    """
    Ejecuta una consulta SQL parametrizada de forma segura
    Previene SQL Injection mediante parametrización
    """
    try:
        if params:
            result = db.session.execute(sql, params)
        else:
            result = db.session.execute(sql)
        
        return result
    except Exception as e:
        logger.error(f"Error ejecutando consulta: {e}")
        raise

def obtener_estadisticas_bd():
    """
    Obtiene estadísticas de la base de datos
    Útil para monitoreo
    """
    try:
        stats = {
            'usuarios': db.session.execute("SELECT COUNT(*) FROM usuarios").scalar(),
            'gastos': db.session.execute("SELECT COUNT(*) FROM gastos").scalar(),
            'ingresos': db.session.execute("SELECT COUNT(*) FROM ingresos").scalar(),
            'objetivos': db.session.execute("SELECT COUNT(*) FROM objetivos_ahorro").scalar()
        }
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas BD: {e}")
        return {}
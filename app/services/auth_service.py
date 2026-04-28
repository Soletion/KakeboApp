"""
Servicio de Autenticación para la aplicación Kakebo
Gestiona la lógica de negocio relacionada con autenticación
Implementa patrones de seguridad y validación
"""
from flask import session
from datetime import datetime, timedelta
import hashlib
import hmac
import logging
from app.utils.database import get_redis

logger = logging.getLogger(__name__)

class AuthService:
    """
    Servicio de autenticación que maneja la lógica de negocio
    Implementa patrones Singleton y Strategy
    """
    
    _instance = None
    _redis_client = None
    
    # Configuración de seguridad
    MAX_INTENTOS_FALLIDOS = 5
    TIEMPO_BLOQUEO_MINUTOS = 15
    
    def __new__(cls):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicialización del servicio"""
        if not hasattr(self, '_inicializado'):
            self._inicializado = True
            self._init_redis()
    
    def _init_redis(self):
        """Inicializa conexión Redis para rate limiting"""
        try:
            self._redis_client = get_redis()
        except Exception as e:
            logger.warning(f"No se pudo conectar a Redis: {e}")
            self._redis_client = None
    
    @classmethod
    def verificar_intentos_login(cls, email):
        """
        Verifica si un email no ha excedido el límite de intentos fallidos
        Implementa rate limiting
        """
        try:
            redis_client = get_redis()
            if not redis_client:
                return True  # Si no hay Redis, permitir siempre
            
            key = f"login_attempts:{email}"
            intentos = redis_client.get(key)
            
            if intentos and int(intentos) >= cls.MAX_INTENTOS_FALLIDOS:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando intentos login: {e}")
            return True  # En caso de error, permitir el intento
    
    @classmethod
    def registrar_intento_fallido(cls, email):
        """
        Registra un intento fallido de login
        """
        try:
            redis_client = get_redis()
            if not redis_client:
                return
            
            key = f"login_attempts:{email}"
            
            # Incrementar contador
            intentos = redis_client.incr(key)
            
            # Establecer expiración en el primer intento
            if intentos == 1:
                redis_client.expire(key, cls.TIEMPO_BLOQUEO_MINUTOS * 60)
            
            logger.warning(f"Intento fallido de login para {email}. Intento {intentos}")
            
        except Exception as e:
            logger.error(f"Error registrando intento fallido: {e}")
    
    @classmethod
    def resetear_intentos_login(cls, email):
        """
        Resetea los intentos fallidos de login para un email
        """
        try:
            redis_client = get_redis()
            if redis_client:
                key = f"login_attempts:{email}"
                redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error reseteando intentos: {e}")
    
    @staticmethod
    def generar_token_reset_password(usuario_id):
        """
        Genera un token seguro para reset de contraseña
        Implementa HMAC para firma
        """
        from app.utils.seguridad import generar_token_seguro
        
        expiracion = datetime.utcnow() + timedelta(hours=24)
        payload = {
            'usuario_id': usuario_id,
            'exp': expiracion.timestamp()
        }
        
        return generar_token_seguro(payload)
    
    @staticmethod
    def verificar_token_reset_password(token):
        """
        Verifica un token de reset de contraseña
        """
        from app.utils.seguridad import verificar_token_seguro
        
        try:
            payload = verificar_token_seguro(token)
            
            # Verificar expiración
            if payload['exp'] < datetime.utcnow().timestamp():
                return None
            
            return payload['usuario_id']
            
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return None
    
    @staticmethod
    def validar_sesion_activa():
        """
        Valida que la sesión actual sea segura
        """
        from flask import session
        
        # Verificar que la sesión tenga los campos necesarios
        if not session.get('_user_id'):
            return False
        
        # Verificar User-Agent consistente
        if session.get('user_agent') != request.user_agent.string:
            return False
        
        # Verificar IP consistente (opcional)
        if session.get('ip_address') != request.remote_addr:
            return False
        
        return True
    
    @staticmethod
    def regenerar_sesion():
        """
        Regenera el ID de sesión por seguridad
        Previene session fixation
        """
        from flask import session
        session.regenerate()
    
    @classmethod
    def obtener_estadisticas_seguridad(cls, usuario_id):
        """
        Obtiene estadísticas de seguridad para un usuario
        """
        try:
            redis_client = get_redis()
            if not redis_client:
                return {}
            
            key = f"login_attempts:{usuario_id}"
            intentos = redis_client.get(key)
            
            return {
                'intentos_fallidos': int(intentos) if intentos else 0,
                'max_intentos': cls.MAX_INTENTOS_FALLIDOS,
                'tiempo_bloqueo': cls.TIEMPO_BLOQUEO_MINUTOS
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
"""
Servicio de Internacionalización (i18n) para la aplicación Kakebo
Gestiona la carga y obtención de traducciones
Implementa patrones Singleton y Factory
"""
import json
import os
from flask import current_app, g
import logging

logger = logging.getLogger(__name__)

class IdiomaService:
    """
    Servicio de internacionalización
    Gestiona las traducciones de la aplicación
    """
    
    _instance = None
    _traducciones = {}
    
    def __new__(cls):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el servicio cargando las traducciones"""
        if not hasattr(self, '_inicializado'):
            self._inicializado = True
            self._cargar_traducciones()
    
    def _cargar_traducciones(self):
        """
        Carga todos los archivos de traducción
        Busca en app/translations/ (carpeta del servidor)
        """
        try:
            # Obtener la ruta absoluta del directorio de traducciones
            # Buscar en diferentes ubicaciones posibles
            posibles_rutas = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations'),  # app/translations
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'translations'),  # app/static/translations
                os.path.join(os.getcwd(), 'app', 'translations'),  # Desde raíz
                os.path.join(os.getcwd(), 'app', 'static', 'translations'),  # Desde raíz
            ]
            
            translations_path = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    translations_path = ruta
                    logger.info(f"Archivos de traducción encontrados en: {translations_path}")
                    break
            
            if not translations_path:
                logger.warning(f"No se encontró el directorio de traducciones en ninguna ubicación")
                return
            
            for archivo in os.listdir(translations_path):
                if archivo.endswith('.json'):
                    idioma = archivo.replace('.json', '')
                    file_path = os.path.join(translations_path, archivo)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self._traducciones[idioma] = json.load(f)
                    
                    logger.info(f"Traducciones cargadas para idioma: {idioma}")
                    
        except Exception as e:
            logger.error(f"Error cargando traducciones: {e}")
    
    def traducir(self, clave, idioma='es', **kwargs):
        """
        Traduce una clave al idioma especificado
        Implementa búsqueda anidada con puntos (ej: 'auth.login.titulo')
        """
        try:
            # Obtener diccionario del idioma
            traducciones = self._traducciones.get(idioma, self._traducciones.get('es', {}))
            
            # Si no hay traducciones cargadas, intentar recargar
            if not traducciones:
                self._cargar_traducciones()
                traducciones = self._traducciones.get(idioma, self._traducciones.get('es', {}))
            
            # Navegar por la clave anidada
            partes = clave.split('.')
            valor = traducciones
            
            for parte in partes:
                if isinstance(valor, dict):
                    valor = valor.get(parte)
                else:
                    valor = None
                    break
            
            # Si no se encuentra, devolver la clave
            if valor is None:
                logger.warning(f"Traducción no encontrada para clave: {clave} en idioma: {idioma}")
                return clave
            
            # Reemplazar parámetros si existen
            if kwargs and isinstance(valor, str):
                try:
                    valor = valor.format(**kwargs)
                except KeyError as e:
                    logger.error(f"Error formateando traducción {clave}: falta parámetro {e}")
            
            return valor
            
        except Exception as e:
            logger.error(f"Error en traducción: {e}")
            return clave
    
    def obtener_idiomas_disponibles(self):
        """Obtiene la lista de idiomas disponibles"""
        return list(self._traducciones.keys())
    
    def obtener_nombre_idioma(self, codigo):
        """Obtiene el nombre nativo de un idioma"""
        nombres = {
            'es': 'Español',
            'en': 'English'
        }
        return nombres.get(codigo, codigo)
    
    def recargar_traducciones(self):
        """Recarga los archivos de traducción (útil en desarrollo)"""
        self._traducciones = {}
        self._cargar_traducciones()
    
    def obtener_traducciones_como_json(self, idioma='es'):
        """Obtiene todas las traducciones de un idioma como JSON"""
        return json.dumps(self._traducciones.get(idioma, {}))
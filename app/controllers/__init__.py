"""
Inicializador del paquete controllers
Exporta todos los blueprints para facilitar importaciones
"""
from app.controllers.auth_controller import auth_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.controllers.gastos_controller import gastos_bp
from app.controllers.ingresos_controller import ingresos_bp
from app.controllers.objetivos_controller import objetivos_bp
from app.controllers.idioma_controller import idioma_bp

# Lista de blueprints para registrar en la aplicación
__all__ = [
    'auth_bp',
    'dashboard_bp',
    'gastos_bp',
    'ingresos_bp',
    'objetivos_bp',
    'idioma_bp'
]

# Función para registrar todos los blueprints
def register_blueprints(app):
    """
    Registra todos los blueprints en la aplicación Flask
    """
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(gastos_bp, url_prefix='/gastos')
    app.register_blueprint(ingresos_bp, url_prefix='/ingresos')
    app.register_blueprint(objetivos_bp, url_prefix='/objetivos')
    app.register_blueprint(idioma_bp, url_prefix='/idioma')
    
    return app
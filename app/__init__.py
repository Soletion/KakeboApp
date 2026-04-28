"""
Módulo de inicialización de la aplicación Flask
Implementa el patrón Factory para crear instancias de la aplicación
"""
from flask import Flask, g, request, session, render_template, flash, redirect, url_for, make_response
from config import Config
from app.extensions import db, login_manager, bcrypt, migrate, csrf
from app.utils.database import init_db
from app.utils.decorators import inject_idioma
import os
import logging
from logging.handlers import RotatingFileHandler


def create_app(config_class=Config):
    """
    Función fábrica que crea y configura la aplicación Flask
    Implementa el patrón Factory
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Cargar configuración
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app) 
    
    # Configurar login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'auth.login_required'
    login_manager.login_message_category = 'warning'
    
    # Registrar blueprints (controladores)
    from app.controllers.auth_controller import auth_bp
    from app.controllers.dashboard_controller import dashboard_bp
    from app.controllers.gastos_controller import gastos_bp
    from app.controllers.ingresos_controller import ingresos_bp
    from app.controllers.objetivos_controller import objetivos_bp
    from app.controllers.idioma_controller import idioma_bp
    from app.controllers.admin_controller import admin_bp
    
    # CAMBIO IMPORTANTE: Dashboard en '/dashboard' en lugar de '/'
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')  # <--- CAMBIADO
    app.register_blueprint(gastos_bp, url_prefix='/gastos')
    app.register_blueprint(ingresos_bp, url_prefix='/ingresos')
    app.register_blueprint(objetivos_bp, url_prefix='/objetivos')
    app.register_blueprint(idioma_bp, url_prefix='/idioma')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Configurar logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/kakebo.log', 
                                         maxBytes=10240, 
                                         backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Kakebo aplicación iniciada')
    
    # Inicializar base de datos y roles
    with app.app_context():
        init_db()
        
        # Inicializar roles en la base de datos
        from app.models.rol import Rol
        Rol.inicializar_roles()
        
        # Crear usuario administrador por defecto si no existe
        from app.models.usuario import Usuario
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@kakebo.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin1234')
        
        admin_existente = Usuario.query.filter_by(email=admin_email).first()
        if not admin_existente:
            rol_admin = Rol.obtener_rol_admin()
            if rol_admin:
                admin = Usuario(
                    email=admin_email,
                    username='admin',
                    nombre='Administrador',
                    apellidos='del Sistema',
                    idioma_preferido='es',
                    rol_id=rol_admin.id
                )
                admin.password = admin_password
                db.session.add(admin)
                db.session.commit()
                app.logger.info(f"Usuario administrador creado: {admin_email}")
    
    # Configurar user_loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    
    # Registrar procesadores de contexto
    @app.context_processor
    def inject_now():
        """Inyecta variables globales en todas las plantillas"""
        from datetime import datetime
        return {
            'now': datetime.now(),
            'app_name': 'Kakebo'
        }
    
    # Procesador para inyectar csrf_token en todas las plantillas
    @app.context_processor
    def inject_csrf_token():
        """Inyecta la función csrf_token en todas las plantillas"""
        from flask_wtf.csrf import generate_csrf
        def csrf_token():
            return generate_csrf()
        return dict(csrf_token=csrf_token)
    
    # Procesador para internacionalización
    @app.context_processor
    def inject_idioma_processor():
        """Inyecta la función de traducción en todas las plantillas"""
        from app.services.idioma_service import IdiomaService
        idioma_service = IdiomaService()
        
        def t(key, **kwargs):
            """Función de traducción para plantillas"""
            idioma = session.get('idioma', request.accept_languages.best_match(['es', 'en']) or 'es')
            return idioma_service.traducir(key, idioma, **kwargs)
        
        return dict(t=t)
    
    # Procesador para inyectar información del usuario
    @app.context_processor
    def inject_user_info():
        """Inyecta información del usuario en todas las plantillas"""
        from flask_login import current_user
        if current_user.is_authenticated:
            return {
                'current_user_rol': current_user.rol.nombre if current_user.rol else None,
                'current_user_es_admin': current_user.es_administrador
            }
        return {}
    
    # ===== MANEJADOR PARA FORZAR NO-CACHE DESPUÉS DE LOGOUT =====
    @app.after_request
    def after_request(response):
        """Añadir headers para evitar caché después de logout"""
        if request.endpoint == 'auth.logout':
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        flash('error.unauthorized', 'error')
        return redirect(url_for('dashboard.index'))
    
    # REDIRECCIÓN DE RAÍZ A DASHBOARD
    @app.route('/')
    def root():
        """Redirige la raíz al dashboard"""
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))
    
    return app


# Importar current_user para usar en context processors
from flask_login import current_user
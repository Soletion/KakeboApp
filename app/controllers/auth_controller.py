"""
Controlador de autenticación para la aplicación Kakebo
Gestiona registro, login, logout y perfil de usuarios
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from app.models.usuario import Usuario
from app.services.auth_service import AuthService
from app.utils.validadores import validar_email, validar_password, validar_username
from app.utils.decorators import logout_required
from app.extensions import db
import logging

# Crear blueprint
auth_bp = Blueprint('auth', __name__)

# Configurar logger
logger = logging.getLogger(__name__)


@auth_bp.route('/registro', methods=['GET', 'POST'])
@logout_required
def registro():
    """
    Vista de registro de nuevos usuarios
    GET: Muestra formulario de registro
    POST: Procesa el registro
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            email = request.form.get('email', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            nombre = request.form.get('nombre', '').strip()
            apellidos = request.form.get('apellidos', '').strip()
            
            # Validar que las contraseñas coincidan
            if password != confirm_password:
                flash('auth.error.password_mismatch', 'error')
                return render_template('auth/registro.html')
            
            # Validar datos
            errores = []
            
            if not validar_email(email):
                errores.append('auth.error.email_invalid')
            
            if not validar_username(username):
                errores.append('auth.error.username_invalid')
            
            if not validar_password(password):
                errores.append('auth.error.password_weak')
            
            if not nombre:
                errores.append('auth.error.name_required')
            
            if errores:
                for error in errores:
                    flash(error, 'error')
                return render_template('auth/registro.html')
            
            # Verificar si el usuario ya existe
            if Usuario.existe_email(email):
                flash('auth.error.email_exists', 'error')
                return render_template('auth/registro.html')
            
            if Usuario.existe_username(username):
                flash('auth.error.username_exists', 'error')
                return render_template('auth/registro.html')
            
            # Crear nuevo usuario
            usuario = Usuario(
                email=email,
                username=username,
                nombre=nombre,
                apellidos=apellidos,
                idioma_preferido=session.get('idioma', 'es')
            )
            usuario.password = password
            
            # Guardar en base de datos
            db.session.add(usuario)
            db.session.commit()
            
            logger.info(f"Nuevo usuario registrado: {username} ({email})")
            
            flash('auth.success.registration', 'success')
            return redirect(url_for('auth.login'))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en registro: {str(e)}")
            flash('auth.error.general', 'error')
    
    return render_template('auth/registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    """
    Vista de inicio de sesión
    GET: Muestra formulario de login
    POST: Procesa el login
    Implementa limitación de intentos fallidos
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            recordar = request.form.get('recordar', False)
            
            # Validar que no estén vacíos
            if not email or not password:
                flash('auth.error.required_fields', 'error')
                return render_template('auth/login.html')
            
            # Verificar límite de intentos
            if not AuthService.verificar_intentos_login(email):
                flash('auth.error.too_many_attempts', 'error')
                return render_template('auth/login.html')
            
            # Buscar usuario por email
            usuario = Usuario.buscar_por_email(email)
            
            # Verificar credenciales
            if usuario and usuario.verificar_password(password):
                if not usuario.activo:
                    flash('auth.error.inactive_account', 'error')
                    return render_template('auth/login.html')
                
                # Iniciar sesión
                login_user(usuario, remember=recordar)
                usuario.actualizar_ultimo_acceso()
                
                # Resetear intentos fallidos
                AuthService.resetear_intentos_login(email)
                
                # Establecer idioma del usuario
                session['idioma'] = usuario.idioma_preferido
                
                logger.info(f"Usuario logueado: {usuario.username}")
                
                flash('auth.success.login', 'success')
                
                # Redirigir a la página solicitada o al dashboard según el rol
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                
                # NUEVO: Redirigir según el rol
                if usuario.es_administrador:
                    return redirect(url_for('admin.dashboard_admin'))
                else:
                    return redirect(url_for('dashboard.index'))
            else:
                # Registrar intento fallido
                AuthService.registrar_intento_fallido(email)
                flash('auth.error.invalid_credentials', 'error')
                
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            flash('auth.error.general', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Cierra la sesión del usuario
    """
    try:
        username = current_user.username if current_user.is_authenticated else "Unknown"
        
        # 1. Cerrar sesión de Flask-Login
        logout_user()
        
        # 2. Limpiar toda la sesión de Flask
        session.clear()
        
        # 3. Eliminar la cookie de sesión manualmente
        response = make_response(redirect(url_for('auth.login')))
        response.set_cookie('session', '', expires=0)
        response.set_cookie('remember_token', '', expires=0)
        
        # 4. Headers anti-caché
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        logger.info(f"Usuario deslogueado: {username}")
        flash('auth.success.logout', 'success')
        
        return response
        
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        flash('auth.error.general', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """
    Vista y edición del perfil de usuario
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            apellidos = request.form.get('apellidos', '').strip()
            email = request.form.get('email', '').strip()
            password_actual = request.form.get('password_actual', '')
            password_nuevo = request.form.get('password_nuevo', '')
            confirmar_password = request.form.get('confirmar_password', '')
            
            # Validar datos
            if not nombre:
                flash('auth.error.name_required', 'error')
                return render_template('auth/perfil.html', usuario=current_user)
            
            if email != current_user.email:
                if not validar_email(email):
                    flash('auth.error.email_invalid', 'error')
                    return render_template('auth/perfil.html', usuario=current_user)
                
                if Usuario.existe_email(email, exclude_id=current_user.id):
                    flash('auth.error.email_exists', 'error')
                    return render_template('auth/perfil.html', usuario=current_user)
            
            # Si se quiere cambiar la contraseña
            if password_nuevo:
                if not password_actual:
                    flash('auth.error.current_password_required', 'error')
                    return render_template('auth/perfil.html', usuario=current_user)
                
                if not current_user.verificar_password(password_actual):
                    flash('auth.error.current_password_invalid', 'error')
                    return render_template('auth/perfil.html', usuario=current_user)
                
                if password_nuevo != confirmar_password:
                    flash('auth.error.password_mismatch', 'error')
                    return render_template('auth/perfil.html', usuario=current_user)
                
                if not validar_password(password_nuevo):
                    flash('auth.error.password_weak', 'error')
                    return render_template('auth/perfil.html', usuario=current_user)
                
                current_user.password = password_nuevo
            
            # Actualizar datos
            current_user.nombre = nombre
            current_user.apellidos = apellidos
            current_user.email = email
            
            db.session.commit()
            
            logger.info(f"Perfil actualizado: {current_user.username}")
            flash('auth.success.profile_updated', 'success')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando perfil: {str(e)}")
            flash('auth.error.general', 'error')
    
    return render_template('auth/perfil.html', usuario=current_user)


@auth_bp.route('/cambiar-idioma', methods=['POST'])
@login_required
def cambiar_idioma():
    """
    Cambia el idioma preferido del usuario
    """
    try:
        idioma = request.form.get('idioma', 'es')
        if idioma in ['es', 'en']:
            current_user.cambiar_idioma(idioma)
            session['idioma'] = idioma
            flash('auth.success.language_changed', 'success')
    except Exception as e:
        logger.error(f"Error cambiando idioma: {str(e)}")
        flash('auth.error.general', 'error')
    
    return redirect(request.referrer or url_for('dashboard.index'))


@auth_bp.route('/recuperar-password', methods=['GET', 'POST'])
@logout_required
def recuperar_password():
    """
    Vista para solicitar recuperación de contraseña
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            
            if not email:
                flash('auth.error.email_required', 'error')
                return render_template('auth/recuperar_password.html')
            
            usuario = Usuario.buscar_por_email(email)
            
            if usuario:
                logger.info(f"Solicitud recuperación password: {email}")
            
            flash('auth.success.recovery_sent', 'info')
            
        except Exception as e:
            logger.error(f"Error en recuperación password: {str(e)}")
            flash('auth.error.general', 'error')
    
    return render_template('auth/recuperar_password.html')


@auth_bp.route('/eliminar-cuenta', methods=['POST'])
@login_required
def eliminar_cuenta():
    """
    Elimina la cuenta del usuario actual
    """
    try:
        usuario = current_user
        username = usuario.username
        
        # Cerrar sesión primero
        logout_user()
        
        # Eliminar usuario de la base de datos
        db.session.delete(usuario)
        db.session.commit()
        
        logger.info(f"Cuenta eliminada: {username}")
        flash('auth.success.account_deleted', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando cuenta: {str(e)}")
        flash('auth.error.general', 'error')
    
    return redirect(url_for('auth.login'))
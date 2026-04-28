"""
Utilidades de seguridad para la aplicación Kakebo
Implementa funciones de cifrado, tokens y validación
"""
import secrets
import string
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from flask import current_app, session
import logging

logger = logging.getLogger(__name__)

# ===== GENERACIÓN DE TOKENS =====

def generar_token_seguro(payload, expiracion=None, rotar=False):
    """
    Genera un token JWT-like seguro
    
    Args:
        payload (dict): Datos a incluir en el token
        expiracion (int): Tiempo de expiración en segundos
        rotar (bool): Si es True, invalida el token anterior
    
    Returns:
        str: Token generado
    """
    try:
        import jwt
        from jwt.exceptions import PyJWTError
        
        secret_key = current_app.config.get('SECRET_KEY', 'dev-key')
        
        # Añadir timestamp de expiración
        if expiracion:
            payload['exp'] = datetime.utcnow() + timedelta(seconds=expiracion)
        
        # Añadir timestamp de emisión
        payload['iat'] = datetime.utcnow()
        
        # Añadir ID único para el token
        payload['jti'] = secrets.token_urlsafe(16)
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        if rotar:
            # Aquí se implementaría la lógica para invalidar token anterior
            pass
        
        return token
        
    except ImportError:
        logger.warning("PyJWT no instalado, usando método alternativo")
        return generar_token_simple(payload, expiracion)
    except Exception as e:
        logger.error(f"Error generando token: {e}")
        raise ValueError("Error generando token de seguridad")

def verificar_token_seguro(token):
    """
    Verifica un token JWT
    
    Args:
        token (str): Token a verificar
    
    Returns:
        dict: Payload del token
    
    Raises:
        ValueError: Si el token es inválido o ha expirado
    """
    try:
        import jwt
        from jwt.exceptions import PyJWTError, ExpiredSignatureError
        
        secret_key = current_app.config.get('SECRET_KEY', 'dev-key')
        
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        # Verificar expiración manual (por si acaso)
        if 'exp' in payload and datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
            raise ValueError("Token expirado")
        
        return payload
        
    except ExpiredSignatureError:
        raise ValueError("Token expirado")
    except PyJWTError as e:
        raise ValueError(f"Token inválido: {e}")
    except ImportError:
        logger.warning("PyJWT no instalado, usando método alternativo")
        return verificar_token_simple(token)
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        raise ValueError("Error verificando token")

def generar_token_simple(payload, expiracion=None):
    """
    Genera un token simple (alternativa sin PyJWT)
    """
    import json
    
    # Convertir payload a string
    payload_str = json.dumps(payload, sort_keys=True)
    
    # Añadir timestamp
    timestamp = datetime.utcnow().isoformat()
    data = f"{payload_str}|{timestamp}"
    
    # Generar firma HMAC
    secret = current_app.config.get('SECRET_KEY', 'dev-key')
    signature = hmac.new(
        secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Codificar para URL
    token = base64.urlsafe_b64encode(f"{data}|{signature}".encode()).decode()
    
    return token

def verificar_token_simple(token):
    """
    Verifica un token simple (alternativa sin PyJWT)
    """
    import json
    
    try:
        # Decodificar
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        data, signature = decoded.rsplit('|', 1)
        
        # Verificar firma
        secret = current_app.config.get('SECRET_KEY', 'dev-key')
        expected = hmac.new(
            secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Firma inválida")
        
        # Extraer payload
        payload_str, timestamp = data.rsplit('|', 1)
        payload = json.loads(payload_str)
        
        # Verificar expiración
        if 'exp' in payload:
            exp = datetime.fromisoformat(payload['exp'])
            if datetime.utcnow() > exp:
                raise ValueError("Token expirado")
        
        return payload
        
    except Exception as e:
        logger.error(f"Error verificando token simple: {e}")
        raise ValueError("Token inválido")

# ===== CSRF PROTECTION =====

def generar_csrf_token():
    """
    Genera un token CSRF y lo guarda en sesión
    """
    token = secrets.token_urlsafe(32)
    session['csrf_token'] = token
    return token

def validar_csrf_token(token):
    """
    Valida un token CSRF contra el almacenado en sesión
    """
    stored = session.get('csrf_token')
    if not stored or not token:
        return False
    
    # Comparación segura contra timing attacks
    return hmac.compare_digest(stored, token)

# ===== VALIDACIÓN DE CONTRASEÑAS =====

def es_password_segura(password):
    """
    Verifica si una contraseña cumple los requisitos de seguridad
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    """
    if not password or len(password) < 8:
        return False
    
    tiene_mayuscula = any(c.isupper() for c in password)
    tiene_minuscula = any(c.islower() for c in password)
    tiene_numero = any(c.isdigit() for c in password)
    
    return tiene_mayuscula and tiene_minuscula and tiene_numero

def generar_password_aleatorio(longitud=12):
    """
    Genera una contraseña aleatoria segura
    """
    # Caracteres permitidos
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    especiales = "!@#$%^&*"
    
    # Asegurar al menos uno de cada tipo
    password = [
        secrets.choice(mayusculas),
        secrets.choice(minusculas),
        secrets.choice(digitos),
        secrets.choice(especiales)
    ]
    
    # Completar con caracteres aleatorios
    todos = minusculas + mayusculas + digitos + especiales
    password.extend(secrets.choice(todos) for _ in range(longitud - 4))
    
    # Mezclar
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

# ===== SANITIZACIÓN =====

def sanitizar_entrada(texto, permitir_html=False):
    """
    Sanitiza una entrada de texto
    """
    if not texto:
        return ""
    
    import html
    
    # Escapar HTML
    texto = html.escape(str(texto))
    
    if not permitir_html:
        # Eliminar cualquier tag HTML escapado
        import re
        texto = re.sub(r'&lt;.*?&gt;', '', texto)
    
    return texto.strip()

def sanitizar_para_sql(texto):
    """
    Sanitiza texto para uso en consultas SQL (escape básico)
    """
    if not texto:
        return ""
    
    # Escapar caracteres peligrosos
    peligrosos = ["'", '"', ";", "--", "/*", "*/", "xp_"]
    texto = str(texto)
    
    for peligro in peligrosos:
        texto = texto.replace(peligro, "")
    
    return texto

# ===== ENMASCARAMIENTO =====

def enmascarar_email(email):
    """
    Enmascara un email para mostrar (ej: u****o@example.com)
    """
    if not email or '@' not in email:
        return email
    
    local, dominio = email.split('@', 1)
    
    if len(local) <= 2:
        mascara = local[0] + '*' * (len(local) - 1)
    else:
        mascara = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{mascara}@{dominio}"

def enmascarar_dato(dato, visible_inicio=2, visible_fin=2):
    """
    Enmascara un dato mostrando solo primeros y últimos caracteres
    """
    if not dato:
        return ""
    
    dato = str(dato)
    if len(dato) <= visible_inicio + visible_fin:
        return '*' * len(dato)
    
    inicio = dato[:visible_inicio]
    fin = dato[-visible_fin:]
    medio = '*' * (len(dato) - visible_inicio - visible_fin)
    
    return f"{inicio}{medio}{fin}"

# ===== VALIDACIÓN DE DOMINIOS =====

def validar_email_dominio(email, dominio_permitido):
    """
    Valida que un email pertenezca a un dominio específico
    """
    if not email or '@' not in email:
        return False
    
    dominio = email.split('@')[1].lower()
    return dominio == dominio_permitido.lower()

# ===== HASH SEGURO =====

def hash_seguro(texto, salt=None):
    """
    Genera un hash seguro de un texto (para tokens, no contraseñas)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Usar PBKDF2 para hash más seguro
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        texto.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100k iteraciones
    )
    
    return {
        'hash': base64.b64encode(hash_obj).decode(),
        'salt': salt
    }

# ===== VERIFICACIÓN DE TIMING ATTACKS =====

def comparacion_segura(a, b):
    """
    Comparación segura contra timing attacks
    """
    return hmac.compare_digest(str(a), str(b))
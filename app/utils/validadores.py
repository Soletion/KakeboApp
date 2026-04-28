"""
Utilidades de validación para la aplicación Kakebo
"""
import re
from datetime import datetime, date

def validar_email(email):
    """Valida formato de email"""
    if not email:
        return False
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_password(password):
    """
    Valida que la contraseña sea segura
    Requisitos: mínimo 8 caracteres, al menos una mayúscula y un número
    """
    if not password or len(password) < 8:
        return False
    tiene_mayuscula = any(c.isupper() for c in password)
    tiene_numero = any(c.isdigit() for c in password)
    return tiene_mayuscula and tiene_numero

def validar_username(username):
    """Valida nombre de usuario (3-20 caracteres, letras, números, _)"""
    if not username:
        return False
    patron = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(patron, username) is not None

def validar_nombre(nombre):
    """Valida nombre (2-50 caracteres, solo letras y espacios)"""
    if not nombre or len(nombre) < 2 or len(nombre) > 50:
        return False
    patron = r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]{2,50}$'
    return re.match(patron, nombre) is not None

def validar_cantidad(cantidad):
    """Valida cantidad monetaria (mayor que 0)"""
    try:
        valor = float(cantidad)
        return valor > 0
    except (ValueError, TypeError):
        return False

def validar_fecha(fecha):
    """Valida fecha (no futura)"""
    if not fecha:
        return False
    try:
        if isinstance(fecha, str):
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        else:
            fecha_obj = fecha
        return fecha_obj <= date.today()
    except (ValueError, TypeError):
        return False

def validar_telefono(telefono):
    """Valida teléfono español (9-15 dígitos)"""
    if not telefono:
        return False
    # Limpiar caracteres no numéricos
    limpio = re.sub(r'[^0-9+]', '', str(telefono))
    return 9 <= len(limpio) <= 15

def validar_dni(dni):
    """Valida DNI español"""
    if not dni:
        return False
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    dni = dni.upper().replace('-', '').replace(' ', '')
    if len(dni) != 9:
        return False
    numeros = dni[:8]
    letra = dni[8]
    if not numeros.isdigit():
        return False
    return letra == letras[int(numeros) % 23]

def validar_codigo_postal(cp):
    """Valida código postal español (5 dígitos)"""
    if not cp:
        return False
    cp_limpio = str(cp).strip()
    if len(cp_limpio) != 5 or not cp_limpio.isdigit():
        return False
    # Rango válido de códigos postales en España (01001-52080)
    codigo = int(cp_limpio)
    return 1001 <= codigo <= 52080

def validar_url_segura(url):
    """Valida que la URL sea segura (https, no localhost)"""
    if not url:
        return False
    patron = r'^https?:\/\/(?!localhost|127\.0\.0\.1|192\.168\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    return re.match(patron, url) is not None

def sanitizar_texto(texto):
    """Sanitiza texto eliminando HTML y caracteres peligrosos"""
    if not texto:
        return ""
    import html
    texto_escapado = html.escape(str(texto))
    return texto_escapado.strip()

def validar_rango_numerico(valor, minimo, maximo):
    """Valida que un número esté en un rango específico"""
    try:
        num = float(valor)
        return minimo <= num <= maximo
    except (ValueError, TypeError):
        return False

def validar_longitud_texto(texto, minimo, maximo):
    """Valida que un texto tenga una longitud específica"""
    if not texto:
        return minimo == 0
    return minimo <= len(str(texto)) <= maximo
"""
Modelo de Usuario para la aplicación Kakebo
Implementa las tablas de usuarios y gestión de autenticación
"""
from app.extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime
import re

class Usuario(UserMixin, db.Model):
    """
    Modelo de Usuario que representa a los usuarios del sistema
    Implementa UserMixin para integración con Flask-Login
    """
    __tablename__ = 'usuarios'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150))
    idioma_preferido = db.Column(db.String(2), default='es')
    
    # NUEVO: Rol del usuario
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, default=1)
    
    # Campos de control
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    # Relaciones (cascada para eliminar datos del usuario)
    gastos = db.relationship('Gasto', backref='usuario', lazy='dynamic', 
                            cascade='all, delete-orphan')
    ingresos = db.relationship('Ingreso', backref='usuario', lazy='dynamic',
                              cascade='all, delete-orphan')
    objetivos = db.relationship('ObjetivoAhorro', backref='usuario', lazy='dynamic',
                               cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Constructor con validación básica"""
        # NUEVO: Si no se especifica rol, asignar rol de usuario por defecto
        if 'rol_id' not in kwargs:
            from app.models.rol import Rol
            rol_usuario = Rol.obtener_rol_usuario()
            if rol_usuario:
                kwargs['rol_id'] = rol_usuario.id
        
        super(Usuario, self).__init__(**kwargs)
        self.validar_datos()
    
    def validar_datos(self):
        """
        Valida los datos del usuario antes de guardar
        Lanza ValueError si algún dato no es válido
        """
        if not self.email or not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Email inválido")
        
        if not self.username or len(self.username) < 3:
            raise ValueError("Username debe tener al menos 3 caracteres")
        
        if not self.nombre:
            raise ValueError("El nombre es obligatorio")
    
    @property
    def password(self):
        """Evita acceso directo a la contraseña"""
        raise AttributeError('La contraseña no es un atributo legible')
    
    @password.setter
    def password(self, password):
        """
        Setter para la contraseña que la hashea automáticamente
        Implementa bcrypt con cost factor 12
        """
        if not password or len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verificar_password(self, password):
        """
        Verifica si la contraseña proporcionada coincide con el hash
        Implementa patrón Strategy para diferentes algoritmos de hash
        """
        if not password:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def actualizar_ultimo_acceso(self):
        """Actualiza la fecha de último acceso"""
        self.ultimo_acceso = datetime.utcnow()
        db.session.commit()
    
    def cambiar_idioma(self, idioma):
        """Cambia el idioma preferido del usuario"""
        if idioma in ['es', 'en']:
            self.idioma_preferido = idioma
            db.session.commit()
            return True
        return False
    
    def get_id(self):
        """Sobrescribe método de UserMixin para usar string"""
        return str(self.id)
    
    @property
    def is_active(self):
        """Sobrescribe propiedad de UserMixin"""
        return self.activo
    
    # NUEVO: Propiedades para verificar roles
    @property
    def es_administrador(self):
        """Verifica si el usuario es administrador"""
        return self.rol and self.rol.nombre == 'administrador'
    
    @property
    def es_usuario_normal(self):
        """Verifica si el usuario es usuario normal"""
        return self.rol and self.rol.nombre == 'usuario'
    
    # NUEVO: Método para cambiar rol (solo para administradores)
    def cambiar_rol(self, nuevo_rol_id):
        """Cambia el rol del usuario"""
        from app.models.rol import Rol
        rol = Rol.query.get(nuevo_rol_id)
        if rol:
            self.rol_id = rol.id
            db.session.commit()
            return True
        return False
    
    def __repr__(self):
        """Representación string del usuario"""
        return f'<Usuario {self.username}>'
    
    def to_dict(self):
        """
        Convierte el usuario a diccionario (patrón Data Transfer Object)
        Útil para APIs y serialización
        """
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'idioma': self.idioma_preferido,
            'rol': self.rol.nombre if self.rol else None,  # NUEVO
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'activo': self.activo
        }
    
    @staticmethod
    def buscar_por_email(email):
        """Método de utilidad para buscar usuario por email"""
        return Usuario.query.filter_by(email=email).first()
    
    @staticmethod
    def buscar_por_username(username):
        """Método de utilidad para buscar usuario por username"""
        return Usuario.query.filter_by(username=username).first()
    
    @staticmethod
    def existe_email(email, exclude_id=None):
        """
        Verifica si un email ya existe en la base de datos
        Útil para validaciones de registro
        """
        query = Usuario.query.filter_by(email=email)
        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)
        return query.first() is not None
    
    @staticmethod
    def existe_username(username, exclude_id=None):
        """
        Verifica si un username ya existe en la base de datos
        Útil para validaciones de registro
        """
        query = Usuario.query.filter_by(username=username)
        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)
        return query.first() is not None
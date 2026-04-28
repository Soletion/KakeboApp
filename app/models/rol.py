"""
Modelo de Rol para la aplicación Kakebo
Define los niveles de acceso de los usuarios
"""
from app.extensions import db
from datetime import datetime

class Rol(db.Model):
    """
    Modelo de Rol que define los permisos de cada usuario
    Implementa RBAC (Role-Based Access Control)
    """
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con usuarios
    usuarios = db.relationship('Usuario', backref='rol', lazy='dynamic')
    
    # Constantes de roles
    ROL_USUARIO = 'usuario'
    ROL_ADMINISTRADOR = 'administrador'
    
    @classmethod
    def obtener_rol_usuario(cls):
        """Obtiene el rol de usuario normal"""
        return cls.query.filter_by(nombre=cls.ROL_USUARIO).first()
    
    @classmethod
    def obtener_rol_admin(cls):
        """Obtiene el rol de administrador"""
        return cls.query.filter_by(nombre=cls.ROL_ADMINISTRADOR).first()
    
    @classmethod
    def inicializar_roles(cls):
        """Inicializa los roles por defecto en la base de datos"""
        roles_existentes = [r.nombre for r in cls.query.all()]
        
        if cls.ROL_USUARIO not in roles_existentes:
            rol_usuario = cls(
                nombre=cls.ROL_USUARIO,
                descripcion='Usuario normal con acceso a sus propias finanzas'
            )
            db.session.add(rol_usuario)
        
        if cls.ROL_ADMINISTRADOR not in roles_existentes:
            rol_admin = cls(
                nombre=cls.ROL_ADMINISTRADOR,
                descripcion='Acceso total para gestión y visualización de todos los usuarios'
            )
            db.session.add(rol_admin)
        
        db.session.commit()
    
    def __repr__(self):
        return f'<Rol {self.nombre}>'
"""
Modelos de datos para Kakebo
Importa todos los modelos para facilitar su uso desde otros módulos
"""

# Intentar importar desde archivos individuales
try:
    from .usuario import Usuario, Rol
except ImportError:
    # Si no existe usuario.py, definir aquí mismo
    from flask_sqlalchemy import SQLAlchemy
    from flask_login import UserMixin
    from datetime import datetime
    
    db = SQLAlchemy()
    
    class Rol(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(50), unique=True, nullable=False)
        descripcion = db.Column(db.String(200))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Rol {self.nombre}>'
    
    class Usuario(UserMixin, db.Model):
        __tablename__ = 'usuarios'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password_hash = db.Column(db.String(200), nullable=False)
        nombre = db.Column(db.String(100))
        apellidos = db.Column(db.String(100))
        idioma_preferido = db.Column(db.String(5), default='es')
        rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=1)
        activo = db.Column(db.Boolean, default=True)
        fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
        ultimo_acceso = db.Column(db.DateTime, default=datetime.utcnow)
        
        rol = db.relationship('Rol', backref='usuarios', foreign_keys=[rol_id])
        
        def __repr__(self):
            return f'<Usuario {self.username}>'

try:
    from .categoria import Categoria
except ImportError:
    class Categoria(db.Model):
        __tablename__ = 'categorias'
        id = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(100))
        nombre_es = db.Column(db.String(100), nullable=False)
        nombre_en = db.Column(db.String(100), nullable=False)
        descripcion = db.Column(db.Text)
        icono = db.Column(db.String(50), default='fa-tag')
        color = db.Column(db.String(7), default='#6c757d')
        
        def __repr__(self):
            return f'<Categoria {self.nombre_es}>'

try:
    from .gasto import Gasto
except ImportError:
    class Gasto(db.Model):
        __tablename__ = 'gastos'
        id = db.Column(db.Integer, primary_key=True)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
        cantidad = db.Column(db.Numeric(10, 2), nullable=False)
        fecha = db.Column(db.Date, nullable=False)
        descripcion = db.Column(db.Text)
        fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
        actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        usuario = db.relationship('Usuario', backref='gastos', foreign_keys=[usuario_id])
        categoria = db.relationship('Categoria', backref='gastos', foreign_keys=[categoria_id])
        
        def __repr__(self):
            return f'<Gasto {self.cantidad} - {self.fecha}>'

try:
    from .ingreso import Ingreso
except ImportError:
    class Ingreso(db.Model):
        __tablename__ = 'ingresos'
        id = db.Column(db.Integer, primary_key=True)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        cantidad = db.Column(db.Numeric(10, 2), nullable=False)
        fecha = db.Column(db.Date, nullable=False)
        descripcion = db.Column(db.Text)
        es_fijo = db.Column(db.Boolean, default=False)
        fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
        actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        usuario = db.relationship('Usuario', backref='ingresos', foreign_keys=[usuario_id])
        
        def __repr__(self):
            return f'<Ingreso {self.cantidad} - {self.fecha}>'

try:
    from .objetivo_ahorro import ObjetivoAhorro
except ImportError:
    class ObjetivoAhorro(db.Model):
        __tablename__ = 'objetivos_ahorro'
        id = db.Column(db.Integer, primary_key=True)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        nombre = db.Column(db.String(100), nullable=False)
        descripcion = db.Column(db.Text)
        cantidad_objetivo = db.Column(db.Numeric(10, 2), nullable=False)
        cantidad_actual = db.Column(db.Numeric(10, 2), default=0)
        fecha_inicio = db.Column(db.Date, nullable=False)
        fecha_limite = db.Column(db.Date, nullable=False)
        estado = db.Column(db.String(20), default='activo')
        fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
        actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        usuario = db.relationship('Usuario', backref='objetivos', foreign_keys=[usuario_id])
        
        def __repr__(self):
            return f'<ObjetivoAhorro {self.nombre} - {self.progreso}%>'
        
        @property
        def progreso(self):
            if self.cantidad_objetivo > 0:
                return min(100, int((self.cantidad_actual / self.cantidad_objetivo) * 100))
            return 0

# Exportar todos los modelos
__all__ = [
    'Usuario',
    'Rol', 
    'Categoria',
    'Gasto',
    'Ingreso',
    'ObjetivoAhorro'
]
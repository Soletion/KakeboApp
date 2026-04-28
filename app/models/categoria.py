"""
Modelo de Categorías para la aplicación Kakebo
Define las categorías fijas del método Kakebo
"""
from app.extensions import db
from datetime import datetime

class Categoria(db.Model):
    """
    Modelo de Categoría que representa las categorías de gastos
    Implementa patrón Repository para acceso a datos
    """
    __tablename__ = 'categorias'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    nombre_es = db.Column(db.String(50), nullable=False)
    nombre_en = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200))
    icono = db.Column(db.String(50), default='fa-question-circle')
    color = db.Column(db.String(7), default='#3498db')  # Código hexadecimal
    
    # Relación con gastos
    gastos = db.relationship('Gasto', backref='categoria_rel', lazy='dynamic')
    
    # Constantes de categorías Kakebo
    CATEGORIAS_FIJAS = [
        {
            'nombre': 'esenciales',
            'nombre_es': 'Gastos esenciales',
            'nombre_en': 'Essential expenses',
            'descripcion': 'Gastos necesarios para vivir (vivienda, comida, servicios)',
            'icono': 'fa-home',
            'color': '#27ae60'
        },
        {
            'nombre': 'prescindibles',
            'nombre_es': 'Gastos prescindibles',
            'nombre_en': 'Discretionary expenses',
            'descripcion': 'Gastos no esenciales pero habituales',
            'icono': 'fa-shopping-bag',
            'color': '#f39c12'
        },
        {
            'nombre': 'ocio',
            'nombre_es': 'Ocio',
            'nombre_en': 'Leisure',
            'descripcion': 'Entretenimiento, viajes, restaurantes',
            'icono': 'fa-film',
            'color': '#3498db'
        },
        {
            'nombre': 'imprevistos',
            'nombre_es': 'Imprevistos',
            'nombre_en': 'Unexpected',
            'descripcion': 'Gastos inesperados y emergencias',
            'icono': 'fa-exclamation-triangle',
            'color': '#e74c3c'
        }
    ]
    
    @classmethod
    def inicializar_categorias(cls):
        """
        Inicializa las categorías por defecto del sistema
        Implementa patrón Factory para crear categorías
        """
        for cat_data in cls.CATEGORIAS_FIJAS:
            categoria = cls.query.filter_by(nombre=cat_data['nombre']).first()
            if not categoria:
                categoria = cls(**cat_data)
                db.session.add(categoria)
        
        db.session.commit()
    
    @classmethod
    def obtener_todas(cls):
        """Obtiene todas las categorías ordenadas"""
        return cls.query.order_by(cls.nombre).all()
    
    @classmethod
    def obtener_por_idioma(cls, idioma='es'):
        """
        Obtiene las categorías con el nombre en el idioma especificado
        Útil para internacionalización
        """
        categorias = cls.obtener_todas()
        for cat in categorias:
            cat.nombre_mostrar = cat.nombre_es if idioma == 'es' else cat.nombre_en
        return categorias
    
    def to_dict(self, idioma='es'):
        """Convierte la categoría a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nombre_mostrar': self.nombre_es if idioma == 'es' else self.nombre_en,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'color': self.color
        }
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'
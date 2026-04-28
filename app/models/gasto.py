"""
Modelo de Gastos para la aplicación Kakebo
Gestiona los gastos de los usuarios
"""
from app.extensions import db
from datetime import datetime

class Gasto(db.Model):
    """
    Modelo de Gasto que representa los gastos de los usuarios
    Implementa validaciones y métodos de utilidad
    """
    __tablename__ = 'gastos'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), 
                          nullable=False, index=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), 
                            nullable=False, index=True)
    
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow().date, index=True)
    descripcion = db.Column(db.String(200))
    
    # Campos de control
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones (definidas en usuario.py y categoria.py)
    
    def __init__(self, **kwargs):
        """Constructor con validaciones"""
        super(Gasto, self).__init__(**kwargs)
        self.validar()
    
    def validar(self):
        """Valida los datos del gasto"""
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        if self.fecha and self.fecha > datetime.utcnow().date():
            raise ValueError("La fecha no puede ser futura")
    
    @property
    def mes(self):
        """Obtiene el mes del gasto (útil para agrupaciones)"""
        return self.fecha.strftime('%Y-%m')
    
    @property
    def año_mes(self):
        """Obtiene año y mes formateado"""
        return self.fecha.strftime('%Y-%m')
    
    @classmethod
    def obtener_por_usuario_y_mes(cls, usuario_id, año, mes):
        """
        Obtiene los gastos de un usuario para un mes específico
        Implementa patrón Repository
        """
        return cls.query.filter_by(usuario_id=usuario_id)\
            .filter(db.extract('year', cls.fecha) == año)\
            .filter(db.extract('month', cls.fecha) == mes)\
            .order_by(cls.fecha.desc()).all()
    
    @classmethod
    def obtener_por_categoria_y_mes(cls, usuario_id, categoria_id, año, mes):
        """
        Obtiene gastos filtrados por categoría y mes
        """
        return cls.query.filter_by(usuario_id=usuario_id, categoria_id=categoria_id)\
            .filter(db.extract('year', cls.fecha) == año)\
            .filter(db.extract('month', cls.fecha) == mes)\
            .all()
    
    @classmethod
    def total_mes(cls, usuario_id, año, mes):
        """
        Calcula el total de gastos para un mes específico
        """
        resultado = cls.query.with_entities(
            db.func.sum(cls.cantidad).label('total')
        ).filter_by(usuario_id=usuario_id)\
         .filter(db.extract('year', cls.fecha) == año)\
         .filter(db.extract('month', cls.fecha) == mes)\
         .first()
        
        return float(resultado.total) if resultado.total else 0
    
    @classmethod
    def total_por_categoria_mes(cls, usuario_id, año, mes):
        """
        Calcula totales por categoría para un mes
        Útil para gráficos y estadísticas
        """
        resultados = cls.query.with_entities(
            cls.categoria_id,
            db.func.sum(cls.cantidad).label('total')
        ).filter_by(usuario_id=usuario_id)\
         .filter(db.extract('year', cls.fecha) == año)\
         .filter(db.extract('month', cls.fecha) == mes)\
         .group_by(cls.categoria_id).all()
        
        return {r.categoria_id: float(r.total) for r in resultados}
    
    @classmethod
    def obtener_ultimos(cls, usuario_id, limite=10):
        """
        Obtiene los últimos gastos de un usuario
        """
        return cls.query.filter_by(usuario_id=usuario_id)\
            .order_by(cls.fecha.desc(), cls.fecha_registro.desc())\
            .limit(limite).all()
    
    @classmethod
    def obtener_ultimos_con_categoria(cls, usuario_id, limite=10):
        """
        Obtiene los últimos gastos de un usuario con información de categoría
        """
        from app.models.categoria import Categoria
        
        gastos = cls.query.filter_by(usuario_id=usuario_id)\
            .order_by(cls.fecha.desc(), cls.fecha_registro.desc())\
            .limit(limite).all()
        
        # Obtener categorías para enriquecer los gastos
        categorias = {c.id: c for c in Categoria.query.all()}
        
        for gasto in gastos:
            if gasto.categoria_id in categorias:
                cat = categorias[gasto.categoria_id]
                gasto.categoria_nombre = cat.nombre_es
                gasto.categoria_color = cat.color
                gasto.categoria_icono = cat.icono
            else:
                gasto.categoria_nombre = 'Sin categoría'
                gasto.categoria_color = '#6c757d'
                gasto.categoria_icono = 'fa-question-circle'
        
        return gastos
    
    @classmethod
    def buscar(cls, usuario_id, **filtros):
        """
        Búsqueda avanzada de gastos con múltiples filtros
        Implementa patrón Specification
        """
        query = cls.query.filter_by(usuario_id=usuario_id)
        
        if 'categoria_id' in filtros and filtros['categoria_id']:
            query = query.filter_by(categoria_id=filtros['categoria_id'])
        
        if 'fecha_desde' in filtros and filtros['fecha_desde']:
            query = query.filter(cls.fecha >= filtros['fecha_desde'])
        
        if 'fecha_hasta' in filtros and filtros['fecha_hasta']:
            query = query.filter(cls.fecha <= filtros['fecha_hasta'])
        
        if 'cantidad_min' in filtros and filtros['cantidad_min']:
            query = query.filter(cls.cantidad >= filtros['cantidad_min'])
        
        if 'cantidad_max' in filtros and filtros['cantidad_max']:
            query = query.filter(cls.cantidad <= filtros['cantidad_max'])
        
        if 'descripcion' in filtros and filtros['descripcion']:
            query = query.filter(cls.descripcion.ilike(f'%{filtros["descripcion"]}%'))
        
        return query.order_by(cls.fecha.desc()).all()
    
    def to_dict(self):
        """Convierte el gasto a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'categoria_id': self.categoria_id,
            'categoria_nombre': self.categoria_rel.nombre_es if self.categoria_rel else None,
            'cantidad': float(self.cantidad),
            'fecha': self.fecha.isoformat(),
            'descripcion': self.descripcion,
            'mes': self.mes
        }
    
    def __repr__(self):
        return f'<Gasto {self.cantidad}€ - {self.fecha}>'
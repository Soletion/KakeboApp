"""
Modelo de Ingresos para la aplicación Kakebo
Gestiona los ingresos de los usuarios
"""
from app.extensions import db
from datetime import datetime

class Ingreso(db.Model):
    """
    Modelo de Ingreso que representa los ingresos de los usuarios
    Distingue entre ingresos fijos y variables
    """
    __tablename__ = 'ingresos'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), 
                          nullable=False, index=True)
    
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow().date, index=True)
    descripcion = db.Column(db.String(200))
    
    # Tipo de ingreso: fijo (mensual) o variable
    es_fijo = db.Column(db.Boolean, default=False)
    
    # Campos de control
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        """Constructor con validaciones"""
        super(Ingreso, self).__init__(**kwargs)
        self.validar()
    
    def validar(self):
        """Valida los datos del ingreso"""
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        if self.fecha and self.fecha > datetime.utcnow().date():
            raise ValueError("La fecha no puede ser futura")
    
    @property
    def mes(self):
        """Obtiene el mes del ingreso"""
        return self.fecha.strftime('%Y-%m')
    
    @classmethod
    def obtener_por_usuario_y_mes(cls, usuario_id, año, mes):
        """
        Obtiene los ingresos de un usuario para un mes específico
        """
        return cls.query.filter_by(usuario_id=usuario_id)\
            .filter(db.extract('year', cls.fecha) == año)\
            .filter(db.extract('month', cls.fecha) == mes)\
            .order_by(cls.fecha.desc()).all()
    
    @classmethod
    def total_mes(cls, usuario_id, año, mes):
        """
        Calcula el total de ingresos para un mes específico
        """
        resultado = cls.query.with_entities(
            db.func.sum(cls.cantidad).label('total')
        ).filter_by(usuario_id=usuario_id)\
         .filter(db.extract('year', cls.fecha) == año)\
         .filter(db.extract('month', cls.fecha) == mes)\
         .first()
        
        return float(resultado.total) if resultado.total else 0
    
    @classmethod
    def ingresos_fijos_mes(cls, usuario_id, año, mes):
        """
        Obtiene solo ingresos fijos de un mes
        """
        return cls.query.filter_by(usuario_id=usuario_id, es_fijo=True)\
            .filter(db.extract('year', cls.fecha) == año)\
            .filter(db.extract('month', cls.fecha) == mes)\
            .all()
    
    @classmethod
    def ingresos_variables_mes(cls, usuario_id, año, mes):
        """
        Obtiene solo ingresos variables de un mes
        """
        return cls.query.filter_by(usuario_id=usuario_id, es_fijo=False)\
            .filter(db.extract('year', cls.fecha) == año)\
            .filter(db.extract('month', cls.fecha) == mes)\
            .all()
    
    @classmethod
    def total_ingresos_fijos(cls, usuario_id):
        """
        Calcula el total de ingresos fijos (para proyecciones)
        """
        resultados = cls.query.with_entities(
            db.func.sum(cls.cantidad).label('total')
        ).filter_by(usuario_id=usuario_id, es_fijo=True).first()
        
        return float(resultados.total) if resultados.total else 0
    
    @classmethod
    def obtener_ultimos(cls, usuario_id, limite=10):
        """
        Obtiene los últimos ingresos de un usuario
        """
        return cls.query.filter_by(usuario_id=usuario_id)\
            .order_by(cls.fecha.desc(), cls.fecha_registro.desc())\
            .limit(limite).all()
    
    @classmethod
    def obtener_ultimos_con_formato(cls, usuario_id, limite=10):
        """
        Obtiene los últimos ingresos con formato para plantilla
        """
        ingresos = cls.query.filter_by(usuario_id=usuario_id)\
            .order_by(cls.fecha.desc(), cls.fecha_registro.desc())\
            .limit(limite).all()
        
        for ingreso in ingresos:
            ingreso.tipo_texto = 'Fijo' if ingreso.es_fijo else 'Variable'
            ingreso.tipo_clase = 'bg-info' if ingreso.es_fijo else 'bg-secondary'
        
        return ingresos
    
    @classmethod
    def buscar(cls, usuario_id, **filtros):
        """
        Búsqueda avanzada de ingresos con múltiples filtros
        """
        query = cls.query.filter_by(usuario_id=usuario_id)
        
        if 'es_fijo' in filtros:
            query = query.filter_by(es_fijo=filtros['es_fijo'])
        
        if 'fecha_desde' in filtros and filtros['fecha_desde']:
            query = query.filter(cls.fecha >= filtros['fecha_desde'])
        
        if 'fecha_hasta' in filtros and filtros['fecha_hasta']:
            query = query.filter(cls.fecha <= filtros['fecha_hasta'])
        
        if 'cantidad_min' in filtros and filtros['cantidad_min']:
            query = query.filter(cls.cantidad >= filtros['cantidad_min'])
        
        if 'descripcion' in filtros and filtros['descripcion']:
            query = query.filter(cls.descripcion.ilike(f'%{filtros["descripcion"]}%'))
        
        return query.order_by(cls.fecha.desc()).all()
    
    def to_dict(self):
        """Convierte el ingreso a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'cantidad': float(self.cantidad),
            'fecha': self.fecha.isoformat(),
            'descripcion': self.descripcion,
            'es_fijo': self.es_fijo,
            'mes': self.mes
        }
    
    def __repr__(self):
        tipo = "Fijo" if self.es_fijo else "Variable"
        return f'<Ingreso {tipo}: {self.cantidad}€ - {self.fecha}>'
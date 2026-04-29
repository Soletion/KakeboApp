"""
Modelo de Objetivos de Ahorro para la aplicación Kakebo
Gestiona las metas de ahorro de los usuarios
"""
from app.extensions import db
from datetime import datetime

class ObjetivoAhorro(db.Model):
    """
    Modelo de Objetivo de Ahorro que representa las metas financieras
    Permite a los usuarios establecer y seguir objetivos de ahorro
    """
    __tablename__ = 'objetivos_ahorro'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), 
                          nullable=False, index=True)
    
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    cantidad_objetivo = db.Column(db.Numeric(10, 2), nullable=False)
    cantidad_actual = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    
    fecha_inicio = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    fecha_limite = db.Column(db.Date, nullable=True)
    
    # Estado del objetivo: activo, completado, cancelado
    estado = db.Column(db.String(20), default='activo', nullable=False)
    
    # Campos de control
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constantes para estados
    ESTADO_ACTIVO = 'activo'
    ESTADO_COMPLETADO = 'completado'
    ESTADO_CANCELADO = 'cancelado'
    
    def __init__(self, **kwargs):
        """Constructor con validaciones"""
        # Asegurar valores por defecto
        if 'cantidad_actual' not in kwargs:
            kwargs['cantidad_actual'] = 0
        if 'estado' not in kwargs:
            kwargs['estado'] = self.ESTADO_ACTIVO
        
        super(ObjetivoAhorro, self).__init__(**kwargs)
        self.validar()
    
    def validar(self):
        """Valida los datos del objetivo"""
        # Validar cantidad objetivo
        if self.cantidad_objetivo <= 0:
            raise ValueError("La cantidad objetivo debe ser mayor a 0")
        
        # Validar cantidad actual (ya no debería ser None)
        if self.cantidad_actual is None:
            self.cantidad_actual = 0
        
        if self.cantidad_actual < 0:
            raise ValueError("La cantidad actual no puede ser negativa")
        
        # Validar fechas (solo si fecha_limite no es None)
        if self.fecha_limite is not None and self.fecha_inicio > self.fecha_limite:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha límite")
        
        # Validar estado
        if self.estado is None:
            self.estado = self.ESTADO_ACTIVO
        
        if self.estado not in [self.ESTADO_ACTIVO, self.ESTADO_COMPLETADO, self.ESTADO_CANCELADO]:
            raise ValueError(f"Estado no válido: {self.estado}")
    
    @property
    def progreso(self):
        """
        Calcula el porcentaje de progreso del objetivo
        """
        if self.cantidad_objetivo == 0:
            return 0
        
        # Asegurar que cantidad_actual no sea None
        cantidad_actual = float(self.cantidad_actual) if self.cantidad_actual is not None else 0
        
        progreso = (cantidad_actual / float(self.cantidad_objetivo)) * 100
        return min(round(progreso, 1), 100)  # No más del 100%
    
    @property
    def dias_restantes(self):
        """
        Calcula los días restantes hasta la fecha límite
        """
        if not self.fecha_limite:
            return None
        
        hoy = datetime.utcnow().date()
        if hoy > self.fecha_limite:
            return 0
        
        return (self.fecha_limite - hoy).days
    
    @property
    def cantidad_restante(self):
        """
        Calcula la cantidad restante para alcanzar el objetivo
        """
        cantidad_actual = float(self.cantidad_actual) if self.cantidad_actual is not None else 0
        restante = float(self.cantidad_objetivo) - cantidad_actual
        return max(restante, 0)  # No negativa
    
    @property
    def esta_completado(self):
        """Verifica si el objetivo está completado"""
        cantidad_actual = float(self.cantidad_actual) if self.cantidad_actual is not None else 0
        return cantidad_actual >= float(self.cantidad_objetivo)
    
    @property
    def esta_vencido(self):
        """Verifica si el objetivo ha vencido"""
        if not self.fecha_limite:
            return False
        return datetime.utcnow().date() > self.fecha_limite
    
    def actualizar_cantidad(self, nueva_cantidad):
        """
        Actualiza la cantidad actual del objetivo
        """
        if nueva_cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa")
        
        self.cantidad_actual = nueva_cantidad
        
        # Actualizar estado si se completó
        if self.esta_completado and self.estado == self.ESTADO_ACTIVO:
            self.estado = self.ESTADO_COMPLETADO
        
        db.session.commit()
    
    def añadir_cantidad(self, cantidad):
        """
        Añade una cantidad al objetivo actual
        """
        if cantidad <= 0:
            raise ValueError("La cantidad a añadir debe ser positiva")
        
        cantidad_actual = float(self.cantidad_actual) if self.cantidad_actual is not None else 0
        nueva_cantidad = cantidad_actual + cantidad
        self.actualizar_cantidad(nueva_cantidad)
    
    def marcar_completado(self):
        """
        Marca el objetivo como completado manualmente
        """
        self.estado = self.ESTADO_COMPLETADO
        db.session.commit()
    
    def cancelar(self):
        """
        Cancela el objetivo
        """
        self.estado = self.ESTADO_CANCELADO
        db.session.commit()
    
    @classmethod
    def obtener_activos(cls, usuario_id):
        """
        Obtiene los objetivos activos de un usuario
        """
        return cls.query.filter_by(usuario_id=usuario_id, estado=cls.ESTADO_ACTIVO)\
            .order_by(cls.fecha_limite).all()
    
    @classmethod
    def obtener_completados(cls, usuario_id):
        """
        Obtiene los objetivos completados de un usuario
        """
        return cls.query.filter_by(usuario_id=usuario_id, estado=cls.ESTADO_COMPLETADO)\
            .order_by(cls.fecha_limite.desc()).all()
    
    @classmethod
    def resumen_objetivos(cls, usuario_id):
        """
        Obtiene un resumen de todos los objetivos del usuario
        """
        activos = cls.obtener_activos(usuario_id)
        completados = cls.obtener_completados(usuario_id)
        
        total_objetivo = sum(float(o.cantidad_objetivo) for o in activos)
        total_actual = sum(float(o.cantidad_actual) for o in activos if o.cantidad_actual is not None)
        
        return {
            'activos': activos,
            'completados': completados,
            'total_objetivo': total_objetivo,
            'total_actual': total_actual,
            'progreso_global': (total_actual / total_objetivo * 100) if total_objetivo > 0 else 0
        }
    
    def to_dict(self):
        """Convierte el objetivo a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'cantidad_objetivo': float(self.cantidad_objetivo),
            'cantidad_actual': float(self.cantidad_actual) if self.cantidad_actual is not None else 0,
            'progreso': self.progreso,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_limite': self.fecha_limite.isoformat() if self.fecha_limite else None,
            'dias_restantes': self.dias_restantes,
            'estado': self.estado,
            'cantidad_restante': self.cantidad_restante,
            'esta_completado': self.esta_completado,
            'esta_vencido': self.esta_vencido
        }
    
    def __repr__(self):
        return f'<Objetivo {self.nombre}: {self.progreso}%>'
"""
Servicio de Cálculos Financieros para la aplicación Kakebo
Gestiona la lógica de negocio para cálculos y estadísticas
Implementa patrones Strategy y Composite
"""
from app.models.gasto import Gasto
from app.models.ingreso import Ingreso
from app.models.objetivo_ahorro import ObjetivoAhorro
from app.models.categoria import Categoria
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

class CalculoService:
    """
    Servicio de cálculos financieros
    Implementa la lógica de negocio para análisis financiero
    """
    
    @staticmethod
    def obtener_resumen_mensual(usuario_id, año, mes):
        """
        Obtiene el resumen financiero completo para un mes específico
        """
        try:
            # Calcular totales
            total_ingresos = Ingreso.total_mes(usuario_id, año, mes)
            total_gastos = Gasto.total_mes(usuario_id, año, mes)
            
            # Calcular ahorro
            ahorro = total_ingresos - total_gastos
            
            # Calcular porcentaje de ahorro
            if total_ingresos > 0:
                porcentaje_ahorro = (ahorro / total_ingresos) * 100
            else:
                porcentaje_ahorro = 0
            
            # Obtener gastos por categoría
            gastos_por_categoria = Gasto.total_por_categoria_mes(usuario_id, año, mes)
            
            # Obtener totales por tipo de ingreso
            ingresos_fijos = sum(
                float(i.cantidad) for i in 
                Ingreso.ingresos_fijos_mes(usuario_id, año, mes)
            )
            
            # Obtener objetivos del mes
            objetivos = ObjetivoAhorro.obtener_activos(usuario_id)
            
            # Calcular media diaria de gastos
            dias_en_mes = (date(año, mes, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            dias_en_mes = dias_en_mes.day
            dias_transcurridos = min(date.today().day, dias_en_mes) if año == date.today().year and mes == date.today().month else dias_en_mes
            
            media_diaria = total_gastos / dias_transcurridos if dias_transcurridos > 0 else 0
            
            # Proyectar gastos mensuales
            proyeccion_mensual = media_diaria * dias_en_mes
            
            return {
                'total_ingresos': total_ingresos,
                'total_gastos': total_gastos,
                'ahorro': ahorro,
                'porcentaje_ahorro': round(porcentaje_ahorro, 1),
                'gastos_por_categoria': gastos_por_categoria,
                'ingresos_fijos': ingresos_fijos,
                'media_diaria': round(media_diaria, 2),
                'proyeccion_mensual': round(proyeccion_mensual, 2),
                'dias_transcurridos': dias_transcurridos,
                'dias_totales': dias_en_mes,
                'objetivos_activos': len(objetivos)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen mensual: {e}")
            return {
                'total_ingresos': 0,
                'total_gastos': 0,
                'ahorro': 0,
                'porcentaje_ahorro': 0,
                'gastos_por_categoria': {},
                'ingresos_fijos': 0,
                'media_diaria': 0,
                'proyeccion_mensual': 0,
                'dias_transcurridos': 0,
                'dias_totales': 0,
                'objetivos_activos': 0
            }
    
    @staticmethod
    def gastos_por_categoria_mes(usuario_id, año, mes):
        """
        Obtiene el desglose de gastos por categoría para un mes
        """
        try:
            resultados = db.session.query(
                Gasto.categoria_id,
                func.sum(Gasto.cantidad).label('total'),
                func.count(Gasto.id).label('cantidad')
            ).filter(
                Gasto.usuario_id == usuario_id,
                extract('year', Gasto.fecha) == año,
                extract('month', Gasto.fecha) == mes
            ).group_by(Gasto.categoria_id).all()
            
            return {
                r.categoria_id: {
                    'total': float(r.total),
                    'cantidad': r.cantidad
                } for r in resultados
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo gastos por categoría: {e}")
            return {}
    
    @staticmethod
    def evolucion_mensual(usuario_id, num_meses=6):
        """
        Obtiene la evolución mensual de ingresos, gastos y ahorro
        """
        try:
            evolucion = []
            fecha_actual = date.today()
            
            for i in range(num_meses - 1, -1, -1):
                fecha = fecha_actual - timedelta(days=30 * i)
                año = fecha.year
                mes = fecha.month
                
                total_ingresos = Ingreso.total_mes(usuario_id, año, mes)
                total_gastos = Gasto.total_mes(usuario_id, año, mes)
                
                evolucion.append({
                    'periodo': f"{año}-{mes:02d}",
                    'nombre': fecha.strftime('%B %Y'),
                    'año': año,
                    'mes': mes,
                    'ingresos': total_ingresos,
                    'gastos': total_gastos,
                    'ahorro': total_ingresos - total_gastos
                })
            
            return evolucion
            
        except Exception as e:
            logger.error(f"Error obteniendo evolución mensual: {e}")
            return []
    
    @staticmethod
    def meses_con_datos(usuario_id):
        """
        Obtiene la lista de meses que tienen datos (gastos o ingresos)
        """
        try:
            # Obtener meses con gastos
            gastos_meses = db.session.query(
                extract('year', Gasto.fecha).label('año'),
                extract('month', Gasto.fecha).label('mes')
            ).filter(Gasto.usuario_id == usuario_id).distinct().all()
            
            # Obtener meses con ingresos
            ingresos_meses = db.session.query(
                extract('year', Ingreso.fecha).label('año'),
                extract('month', Ingreso.fecha).label('mes')
            ).filter(Ingreso.usuario_id == usuario_id).distinct().all()
            
            # Combinar y eliminar duplicados
            meses_set = set()
            for año, mes in gastos_meses + ingresos_meses:
                meses_set.add((int(año), int(mes)))
            
            # Ordenar cronológicamente
            meses = [{'año': a, 'mes': m} for a, m in sorted(meses_set, reverse=True)]
            
            return meses
            
        except Exception as e:
            logger.error(f"Error obteniendo meses con datos: {e}")
            return []
    
    @staticmethod
    def todos_los_meses_con_datos(usuario_id):
        """
        Similar a meses_con_datos pero con formato más completo
        """
        try:
            meses = CalculoService.meses_con_datos(usuario_id)
            
            for mes in meses:
                fecha = date(mes['año'], mes['mes'], 1)
                mes['nombre'] = fecha.strftime('%B %Y')
                mes['fecha'] = fecha.isoformat()
            
            return meses
            
        except Exception as e:
            logger.error(f"Error obteniendo todos los meses: {e}")
            return []
    
    @staticmethod
    def comparativa_anual(usuario_id, año):
        """
        Obtiene comparativa mensual para un año específico
        """
        try:
            comparativa = []
            
            for mes in range(1, 13):
                ingresos = Ingreso.total_mes(usuario_id, año, mes)
                gastos = Gasto.total_mes(usuario_id, año, mes)
                
                comparativa.append({
                    'mes': mes,
                    'nombre_mes': date(año, mes, 1).strftime('%B'),
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'ahorro': ingresos - gastos
                })
            
            return comparativa
            
        except Exception as e:
            logger.error(f"Error obteniendo comparativa anual: {e}")
            return []
    
    @staticmethod
    def categorias_mas_gasto(usuario_id, año, mes, limite=5):
        """
        Obtiene las categorías con más gasto en un mes
        """
        try:
            gastos_por_categoria = CalculoService.gastos_por_categoria_mes(usuario_id, año, mes)
            
            # Obtener nombres de categorías
            categorias = {c.id: c for c in Categoria.query.all()}
            
            # Crear lista y ordenar
            lista = []
            for cat_id, datos in gastos_por_categoria.items():
                categoria = categorias.get(cat_id)
                if categoria:
                    lista.append({
                        'categoria_id': cat_id,
                        'categoria_nombre': categoria.nombre_es,
                        'categoria_color': categoria.color,
                        'total': datos['total'],
                        'cantidad': datos['cantidad']
                    })
            
            # Ordenar por total descendente
            lista.sort(key=lambda x: x['total'], reverse=True)
            
            return lista[:limite]
            
        except Exception as e:
            logger.error(f"Error obteniendo categorías con más gasto: {e}")
            return []
    
    @staticmethod
    def calcular_tendencia(usuario_id):
        """
        Calcula la tendencia de gastos (creciente, decreciente, estable)
        """
        try:
            # Obtener últimos 3 meses
            evolucion = CalculoService.evolucion_mensual(usuario_id, 3)
            
            if len(evolucion) < 3:
                return 'estable'
            
            gastos = [m['gastos'] for m in evolucion]
            
            # Calcular pendiente
            if gastos[2] > gastos[1] > gastos[0]:
                return 'creciente'
            elif gastos[2] < gastos[1] < gastos[0]:
                return 'decreciente'
            else:
                return 'estable'
                
        except Exception as e:
            logger.error(f"Error calculando tendencia: {e}")
            return 'estable'
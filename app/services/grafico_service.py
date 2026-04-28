"""
Servicio de Gráficos para la aplicación Kakebo
Prepara datos para visualización con Chart.js
Implementa patrones Factory y Adapter
"""
import logging

logger = logging.getLogger(__name__)

class GraficoService:
    """
    Servicio que prepara datos para diferentes tipos de gráficos
    Actúa como adaptador entre los datos del modelo y Chart.js
    """
    
    @staticmethod
    def preparar_datos_gastos_categoria(gastos_por_categoria, categorias):
        """
        Prepara datos para gráfico de pastel de gastos por categoría
        """
        try:
            labels = []
            data = []
            background_colors = []
            
            for categoria in categorias:
                total = gastos_por_categoria.get(categoria.id, {}).get('total', 0)
                if total > 0:
                    labels.append(categoria.nombre_mostrar)
                    data.append(total)
                    background_colors.append(categoria.color)
            
            return {
                'type': 'doughnut',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': data,
                        'backgroundColor': background_colors,
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {
                            'position': 'bottom'
                        },
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return context.raw.toFixed(2) + "€"; }'
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparando datos gráfico categorías: {e}")
            return {
                'type': 'doughnut',
                'data': {'labels': [], 'datasets': [{'data': []}]}
            }
    
    @staticmethod
    def preparar_datos_evolucion(evolucion_mensual):
        """
        Prepara datos para gráfico de línea de evolución mensual
        """
        try:
            labels = [e['nombre'] for e in evolucion_mensual]
            ingresos = [e['ingresos'] for e in evolucion_mensual]
            gastos = [e['gastos'] for e in evolucion_mensual]
            ahorros = [e['ahorro'] for e in evolucion_mensual]
            
            return {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Ingresos',
                            'data': ingresos,
                            'borderColor': '#27ae60',
                            'backgroundColor': 'rgba(39, 174, 96, 0.1)',
                            'tension': 0.1
                        },
                        {
                            'label': 'Gastos',
                            'data': gastos,
                            'borderColor': '#e74c3c',
                            'backgroundColor': 'rgba(231, 76, 60, 0.1)',
                            'tension': 0.1
                        },
                        {
                            'label': 'Ahorro',
                            'data': ahorros,
                            'borderColor': '#3498db',
                            'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                            'tension': 0.1
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {
                            'position': 'bottom'
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return value + "€"; }'
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparando datos evolución: {e}")
            return {
                'type': 'line',
                'data': {'labels': [], 'datasets': []}
            }
    
    @staticmethod
    def preparar_datos_comparativa_anual(comparativa):
        """
        Prepara datos para gráfico de barras de comparativa anual
        """
        try:
            labels = [c['nombre_mes'] for c in comparativa]
            ingresos = [c['ingresos'] for c in comparativa]
            gastos = [c['gastos'] for c in comparativa]
            
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Ingresos',
                            'data': ingresos,
                            'backgroundColor': '#27ae60',
                            'borderColor': '#229954',
                            'borderWidth': 1
                        },
                        {
                            'label': 'Gastos',
                            'data': gastos,
                            'backgroundColor': '#e74c3c',
                            'borderColor': '#c0392b',
                            'borderWidth': 1
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {
                            'position': 'bottom'
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return value + "€"; }'
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparando datos comparativa: {e}")
            return {
                'type': 'bar',
                'data': {'labels': [], 'datasets': []}
            }
    
    @staticmethod
    def preparar_datos_evolucion_historica(datos_historicos):
        """
        Prepara datos para gráfico de evolución histórica
        """
        try:
            labels = [d['nombre'] for d in datos_historicos]
            ahorros = [d['ahorro'] for d in datos_historicos]
            
            # Determinar color basado en ahorro positivo/negativo
            background_colors = [
                '#27ae60' if a >= 0 else '#e74c3c' for a in ahorros
            ]
            
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Ahorro',
                        'data': ahorros,
                        'backgroundColor': background_colors,
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {
                            'display': False
                        },
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return "Ahorro: " + context.raw.toFixed(2) + "€"; }'
                            }
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return value + "€"; }'
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparando datos histórico: {e}")
            return {
                'type': 'bar',
                'data': {'labels': [], 'datasets': []}
            }
    
    @staticmethod
    def preparar_datos_objetivos(objetivos):
        """
        Prepara datos para gráfico de progreso de objetivos
        """
        try:
            labels = [o.nombre for o in objetivos]
            progreso = [o.progreso for o in objetivos]
            
            return {
                'type': 'progress',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': progreso,
                        'backgroundColor': '#3498db'
                    }]
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparando datos objetivos: {e}")
            return {
                'type': 'progress',
                'data': {'labels': [], 'datasets': [{'data': []}]}
            }
    
    @staticmethod
    def preparar_datos_distribucion_gastos(gastos_por_categoria, total_gastos):
        """
        Prepara datos para gráfico de distribución de gastos
        """
        try:
            datos = []
            for cat_id, datos_cat in gastos_por_categoria.items():
                porcentaje = (datos_cat['total'] / total_gastos * 100) if total_gastos > 0 else 0
                datos.append({
                    'categoria_id': cat_id,
                    'total': datos_cat['total'],
                    'cantidad': datos_cat['cantidad'],
                    'porcentaje': round(porcentaje, 1)
                })
            
            # Ordenar por total descendente
            datos.sort(key=lambda x: x['total'], reverse=True)
            
            return datos
            
        except Exception as e:
            logger.error(f"Error preparando datos distribución: {e}")
            return []
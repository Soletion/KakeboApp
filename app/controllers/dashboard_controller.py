"""
Controlador del Dashboard principal para la aplicación Kakebo
Muestra resúmenes, gráficos y estadísticas financieras
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, flash
from flask_login import login_required, current_user
from app.services.calculo_service import CalculoService
from app.services.grafico_service import GraficoService
from app.models.gasto import Gasto
from app.models.ingreso import Ingreso
from app.models.objetivo_ahorro import ObjetivoAhorro
from app.models.categoria import Categoria
from datetime import datetime, date
import logging
import sys

# Crear blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Configurar logger
logger = logging.getLogger(__name__)

# FORZAR LOG A CONSOLA INMEDIATAMENTE
print("=" * 60)
print("¡CONTROLADOR DASHBOARD CARGADO correctamente!")
print(f"Blueprint: {dashboard_bp.name}")
print(f"URL prefix: {dashboard_bp.url_prefix}")
print("=" * 60, flush=True)


@dashboard_bp.route('/')
@login_required
def index():
    """
    Página principal del dashboard
    Muestra resumen del mes actual y últimos movimientos
    """
    print(f"🐛 [DASHBOARD] Función index EJECUTADA - Usuario: {current_user.id if current_user.is_authenticated else 'No autenticado'}", flush=True)
    logger.info(f"Acceso al dashboard - Usuario ID: {current_user.id}")
    
    # Si es administrador, redirigir al panel de admin
    if current_user.es_administrador:
        print(f"🐛 [DASHBOARD] Usuario administrador, redirigiendo a admin panel", flush=True)
        return redirect(url_for('admin.dashboard_admin'))
    
    try:
        # Obtener año y mes actual
        hoy = date.today()
        año = hoy.year
        mes = hoy.month
        print(f"🐛 [DASHBOARD] Año: {año}, Mes: {mes}", flush=True)
        
        # Obtener resumen financiero
        print(f"🐛 [DASHBOARD] Llamando a CalculoService.obtener_resumen_mensual...", flush=True)
        resumen = CalculoService.obtener_resumen_mensual(current_user.id, año, mes)
        print(f"🐛 [DASHBOARD] Resumen obtenido: {resumen}", flush=True)
        
        # Obtener últimos gastos
        print(f"🐛 [DASHBOARD] Llamando a Gasto.obtener_ultimos...", flush=True)
        ultimos_gastos = Gasto.obtener_ultimos(current_user.id, 5)
        print(f"🐛 [DASHBOARD] Gastos obtenidos: {len(ultimos_gastos)}", flush=True)
        
        # Obtener últimos ingresos
        ultimos_ingresos = Ingreso.obtener_ultimos(current_user.id, 5)
        print(f"🐛 [DASHBOARD] Ingresos obtenidos: {len(ultimos_ingresos)}", flush=True)
        
        # Obtener objetivos activos
        objetivos = ObjetivoAhorro.obtener_activos(current_user.id)
        print(f"🐛 [DASHBOARD] Objetivos obtenidos: {len(objetivos)}", flush=True)
        
        # Obtener datos para gráficos
        gastos_por_categoria = CalculoService.gastos_por_categoria_mes(
            current_user.id, año, mes
        )
        print(f"🐛 [DASHBOARD] Gastos por categoría: {len(gastos_por_categoria)} categorías", flush=True)
        
        # Preparar datos para gráfico de categorías
        categorias = Categoria.obtener_por_idioma(session.get('idioma', 'es'))
        datos_grafico = GraficoService.preparar_datos_gastos_categoria(
            gastos_por_categoria, categorias
        )
        
        # Preparar datos para gráfico de evolución mensual (últimos 6 meses)
        evolucion = CalculoService.evolucion_mensual(current_user.id, 6)
        datos_evolucion = GraficoService.preparar_datos_evolucion(evolucion)
        
        print(f"🐛 [DASHBOARD] Renderizando template con resumen.total_ingresos={resumen.get('total_ingresos', 0)}", flush=True)
        
        return render_template(
            'dashboard/index.html',
            resumen=resumen,
            ultimos_gastos=ultimos_gastos,
            ultimos_ingresos=ultimos_ingresos,
            objetivos=objetivos,
            datos_grafico=datos_grafico,
            datos_evolucion=datos_evolucion,
            mes_actual=f"{año}-{mes:02d}",
            año=año,
            mes=mes
        )
        
    except Exception as e:
        print(f"❌ [DASHBOARD] ERROR: {str(e)}", flush=True)
        logger.error(f"Error cargando dashboard: {str(e)}", exc_info=True)
        # Crear un resumen vacío para evitar el error
        resumen_vacio = {
            'total_ingresos': 0,
            'total_gastos': 0,
            'ahorro': 0,
            'porcentaje_ahorro': 0,
            'gastos_por_categoria': {},
            'ingresos_fijos': 0,
            'media_diaria': 0,
            'proyeccion_mensual': 0,
            'dias_transcurridos': 0,
            'dias_totales': 30,
            'objetivos_activos': 0
        }
        return render_template(
            'dashboard/index.html', 
            resumen=resumen_vacio,
            ultimos_gastos=[],
            ultimos_ingresos=[],
            objetivos=[],
            datos_grafico={'data': {'labels': [], 'datasets': [{'data': []}]}},
            datos_evolucion={'data': {'labels': [], 'datasets': []}},
            mes_actual=f"{date.today().year}-{date.today().month:02d}",
            año=date.today().year,
            mes=date.today().month,
            error='dashboard.error.general'
        )


@dashboard_bp.route('/resumen-mensual')
@login_required
def resumen_mensual():
    """
    Vista detallada del resumen mensual
    Permite seleccionar mes y año
    """
    try:
        # Obtener parámetros de la URL
        año = request.args.get('año', type=int)
        mes = request.args.get('mes', type=int)
        
        # Si no se especifican, usar mes actual
        if not año or not mes:
            hoy = date.today()
            año = hoy.year
            mes = hoy.month
        
        # Validar mes
        if mes < 1 or mes > 12:
            flash('dashboard.error.invalid_month', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Obtener resumen del mes seleccionado
        resumen = CalculoService.obtener_resumen_mensual(current_user.id, año, mes)
        
        # Obtener gastos detallados del mes
        gastos = Gasto.obtener_por_usuario_y_mes(current_user.id, año, mes)
        
        # Obtener ingresos detallados del mes
        ingresos = Ingreso.obtener_por_usuario_y_mes(current_user.id, año, mes)
        
        # Obtener totales por categoría
        gastos_por_categoria = CalculoService.gastos_por_categoria_mes(
            current_user.id, año, mes
        )
        
        # Obtener categorías con nombres localizados
        categorias = Categoria.obtener_por_idioma(session.get('idioma', 'es'))
        
        # Enriquecer gastos con información de categoría
        gastos_con_categoria = []
        for gasto in gastos:
            gasto_dict = gasto.to_dict()
            categoria = next((c for c in categorias if c.id == gasto.categoria_id), None)
            if categoria:
                gasto_dict['categoria_nombre'] = categoria.nombre_mostrar
                gasto_dict['categoria_color'] = categoria.color
            gastos_con_categoria.append(gasto_dict)
        
        # Calcular meses disponibles
        meses_disponibles = CalculoService.meses_con_datos(current_user.id)
        
        return render_template(
            'dashboard/resumen_mensual.html',
            resumen=resumen,
            gastos=gastos_con_categoria,
            ingresos=ingresos,
            gastos_por_categoria=gastos_por_categoria,
            categorias=categorias,
            año_seleccionado=año,
            mes_seleccionado=mes,
            meses_disponibles=meses_disponibles,
            nombre_mes=datetime(año, mes, 1).strftime('%B').capitalize()
        )
        
    except Exception as e:
        logger.error(f"Error cargando resumen mensual: {str(e)}", exc_info=True)
        flash('dashboard.error.general', 'error')
        return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/historico')
@login_required
def historico():
    """
    Vista del histórico de meses anteriores
    Muestra evolución temporal
    """
    try:
        # Obtener todos los meses con datos
        meses = CalculoService.todos_los_meses_con_datos(current_user.id)
        
        # Preparar datos para gráfico histórico
        datos_historicos = []
        for mes_data in meses:
            resumen = CalculoService.obtener_resumen_mensual(
                current_user.id, 
                mes_data['año'], 
                mes_data['mes']
            )
            datos_historicos.append({
                'periodo': f"{mes_data['año']}-{mes_data['mes']:02d}",
                'nombre': datetime(mes_data['año'], mes_data['mes'], 1).strftime('%B %Y'),
                'ingresos': resumen['total_ingresos'],
                'gastos': resumen['total_gastos'],
                'ahorro': resumen['ahorro'],
                'porcentaje_ahorro': resumen['porcentaje_ahorro']
            })
        
        # Ordenar cronológicamente
        datos_historicos.sort(key=lambda x: x['periodo'])
        
        # Preparar datos para gráfico de evolución
        datos_evolucion = GraficoService.preparar_datos_evolucion_historica(datos_historicos)
        
        return render_template(
            'dashboard/historico.html',
            datos_historicos=datos_historicos,
            datos_evolucion=datos_evolucion
        )
        
    except Exception as e:
        logger.error(f"Error cargando histórico: {str(e)}", exc_info=True)
        flash('dashboard.error.general', 'error')
        return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/api/resumen-mes')
@login_required
def api_resumen_mes():
    """
    API endpoint para obtener resumen mensual (AJAX)
    """
    try:
        año = request.args.get('año', type=int)
        mes = request.args.get('mes', type=int)
        
        if not año or not mes:
            hoy = date.today()
            año = hoy.year
            mes = hoy.month
        
        resumen = CalculoService.obtener_resumen_mensual(current_user.id, año, mes)
        return jsonify({'success': True, 'data': resumen})
        
    except Exception as e:
        logger.error(f"Error en API resumen mes: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/gastos-por-categoria')
@login_required
def api_gastos_por_categoria():
    """
    API endpoint para obtener gastos por categoría (AJAX)
    """
    try:
        año = request.args.get('año', type=int)
        mes = request.args.get('mes', type=int)
        
        if not año or not mes:
            hoy = date.today()
            año = hoy.year
            mes = hoy.month
        
        gastos_por_categoria = CalculoService.gastos_por_categoria_mes(
            current_user.id, año, mes
        )
        
        categorias = Categoria.obtener_por_idioma(session.get('idioma', 'es'))
        datos_grafico = GraficoService.preparar_datos_gastos_categoria(
            gastos_por_categoria, categorias
        )
        
        return jsonify({'success': True, 'data': datos_grafico})
        
    except Exception as e:
        logger.error(f"Error en API gastos por categoria: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# RUTA DE PRUEBA PARA VERIFICAR QUE EL BLUEPRINT FUNCIONA
@dashboard_bp.route('/test')
@login_required
def test():
    """
    Ruta de prueba para verificar que el dashboard blueprint funciona
    """
    print("🐛 [TEST] Ruta de prueba ejecutada!", flush=True)
    return jsonify({
        'success': True,
        'message': 'Dashboard blueprint funciona correctamente',
        'user_id': current_user.id,
        'user_email': current_user.email
    })
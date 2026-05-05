"""
Fixtures y datos de prueba para tests
Proporciona datos prefabricados para usar en tests
"""
import pytest
from app.models import Usuario, Categoria, Gasto, Ingreso, ObjetivoAhorro
from datetime import date, timedelta, datetime
import random

@pytest.fixture
def datos_usuarios_prueba():
    """Datos de usuarios de prueba"""
    return [
        {
            'email': 'usuario1@test.com',
            'username': 'usuario1',
            'nombre': 'Usuario',
            'apellidos': 'Uno',
            'password': 'Test1234'
        },
        {
            'email': 'usuario2@test.com',
            'username': 'usuario2',
            'nombre': 'Usuario',
            'apellidos': 'Dos',
            'password': 'Test1234'
        },
        {
            'email': 'usuario3@test.com',
            'username': 'usuario3',
            'nombre': 'Usuario',
            'apellidos': 'Tres',
            'password': 'Test1234'
        }
    ]

@pytest.fixture
def datos_gastos_prueba(usuario_base, categorias_base):
    """Datos de gastos de prueba"""
    gastos = []
    hoy = date.today()
    
    for i in range(20):
        gasto = {
            'usuario_id': usuario_base.id,
            'categoria_id': random.choice(categorias_base).id,
            'cantidad': round(random.uniform(10, 500), 2),
            'fecha': hoy - timedelta(days=random.randint(0, 90)),
            'descripcion': f'Gasto de prueba {i+1}'
        }
        gastos.append(gasto)
    
    return gastos

@pytest.fixture
def datos_ingresos_prueba(usuario_base):
    """Datos de ingresos de prueba"""
    ingresos = []
    hoy = date.today()
    
    # Ingresos fijos (cada mes)
    for i in range(3):
        for mes in range(1, 4):
            ingreso = {
                'usuario_id': usuario_base.id,
                'cantidad': round(random.uniform(1000, 2000), 2),
                'fecha': date(hoy.year, mes, random.randint(1, 28)),
                'descripcion': f'Ingreso fijo {i+1}',
                'es_fijo': True
            }
            ingresos.append(ingreso)
    
    # Ingresos variables
    for i in range(10):
        ingreso = {
            'usuario_id': usuario_base.id,
            'cantidad': round(random.uniform(100, 500), 2),
            'fecha': hoy - timedelta(days=random.randint(0, 90)),
            'descripcion': f'Ingreso variable {i+1}',
            'es_fijo': False
        }
        ingresos.append(ingreso)
    
    return ingresos

@pytest.fixture
def datos_objetivos_prueba(usuario_base):
    """Datos de objetivos de prueba"""
    objetivos = []
    hoy = date.today()
    
    # Objetivo activo
    objetivos.append({
        'usuario_id': usuario_base.id,
        'nombre': 'Ahorro para vacaciones',
        'descripcion': 'Viaje a la playa',
        'cantidad_objetivo': 1500.00,
        'cantidad_actual': 750.00,
        'fecha_inicio': hoy - timedelta(days=30),
        'fecha_limite': hoy + timedelta(days=60),
        'estado': 'activo'
    })
    
    # Objetivo completado
    objetivos.append({
        'usuario_id': usuario_base.id,
        'nombre': 'Fondo de emergencia',
        'descripcion': 'Ahorro para imprevistos',
        'cantidad_objetivo': 1000.00,
        'cantidad_actual': 1000.00,
        'fecha_inicio': hoy - timedelta(days=90),
        'fecha_limite': hoy - timedelta(days=10),
        'estado': 'completado'
    })
    
    # Objetivo a largo plazo
    objetivos.append({
        'usuario_id': usuario_base.id,
        'nombre': 'Compra de coche',
        'descripcion': 'Ahorrar para coche nuevo',
        'cantidad_objetivo': 5000.00,
        'cantidad_actual': 1200.00,
        'fecha_inicio': hoy - timedelta(days=180),
        'fecha_limite': hoy + timedelta(days=365),
        'estado': 'activo'
    })
    
    return objetivos

@pytest.fixture
def datos_completos_prueba(session, datos_usuarios_prueba, categorias_base):
    """Fixture que crea un conjunto completo de datos de prueba"""
    usuarios = []
    
    for data in datos_usuarios_prueba:
        usuario = Usuario(
            email=data['email'],
            username=data['username'],
            nombre=data['nombre'],
            apellidos=data['apellidos']
        )
        usuario.password = data['password']
        session.add(usuario)
        usuarios.append(usuario)
    
    session.commit()
    
    # Crear gastos para cada usuario
    for usuario in usuarios:
        for i in range(15):
            gasto = Gasto(
                usuario_id=usuario.id,
                categoria_id=random.choice(categorias_base).id,
                cantidad=round(random.uniform(10, 300), 2),
                fecha=date.today() - timedelta(days=random.randint(0, 60)),
                descripcion=f'Gasto {i} de {usuario.username}'
            )
            session.add(gasto)
        
        # Crear ingresos para cada usuario
        for i in range(5):
            ingreso = Ingreso(
                usuario_id=usuario.id,
                cantidad=round(random.uniform(500, 2000), 2),
                fecha=date.today() - timedelta(days=random.randint(0, 60)),
                descripcion=f'Ingreso {i} de {usuario.username}',
                es_fijo=(i < 2)
            )
            session.add(ingreso)
        
        # Crear objetivo para cada usuario
        objetivo = ObjetivoAhorro(
            usuario_id=usuario.id,
            nombre=f'Objetivo de {usuario.username}',
            cantidad_objetivo=2000.00,
            cantidad_actual=500.00,
            fecha_inicio=date.today() - timedelta(days=30)
        )
        session.add(objetivo)
    
    session.commit()
    return usuarios

@pytest.fixture
def escenario_mensual_completo(session, usuario_base, categorias_base):
    """
    Crea un escenario mensual completo con:
    - Ingresos fijos y variables
    - Gastos de todas las categorías
    - Objetivos activos
    """
    hoy = date.today()
    año = hoy.year
    mes = hoy.month
    
    # Ingresos del mes
    ingresos = [
        Ingreso(
            usuario_id=usuario_base.id,
            cantidad=1800.00,
            fecha=date(año, mes, 1),
            descripcion='Nómina',
            es_fijo=True
        ),
        Ingreso(
            usuario_id=usuario_base.id,
            cantidad=250.00,
            fecha=date(año, mes, 15),
            descripcion='Freelance',
            es_fijo=False
        )
    ]
    
    # Gastos del mes
    gastos = [
        Gasto(
            usuario_id=usuario_base.id,
            categoria_id=categorias_base[0].id,  # Esenciales
            cantidad=650.00,
            fecha=date(año, mes, 5),
            descripcion='Alquiler'
        ),
        Gasto(
            usuario_id=usuario_base.id,
            categoria_id=categorias_base[0].id,  # Esenciales
            cantidad=150.00,
            fecha=date(año, mes, 10),
            descripcion='Supermercado'
        ),
        Gasto(
            usuario_id=usuario_base.id,
            categoria_id=categorias_base[1].id,  # Prescindibles
            cantidad=80.00,
            fecha=date(año, mes, 12),
            descripcion='Ropa'
        ),
        Gasto(
            usuario_id=usuario_base.id,
            categoria_id=categorias_base[2].id,  # Ocio
            cantidad=45.00,
            fecha=date(año, mes, 20),
            descripcion='Cine y cena'
        ),
        Gasto(
            usuario_id=usuario_base.id,
            categoria_id=categorias_base[3].id,  # Imprevistos
            cantidad=90.00,
            fecha=date(año, mes, 25),
            descripcion='Farmacia'
        )
    ]
    
    # Objetivos
    objetivos = [
        ObjetivoAhorro(
            usuario_id=usuario_base.id,
            nombre='Ahorro mensual',
            cantidad_objetivo=500.00,
            cantidad_actual=300.00,
            fecha_inicio=date(año, mes, 1)
        )
    ]
    
    for item in ingresos + gastos + objetivos:
        session.add(item)
    
    session.commit()
    
    return {
        'ingresos': ingresos,
        'gastos': gastos,
        'objetivos': objetivos,
        'total_ingresos': sum(float(i.cantidad) for i in ingresos),
        'total_gastos': sum(float(g.cantidad) for g in gastos)
    }

@pytest.fixture
def escenario_historico(session, usuario_base, categorias_base):
    """
    Crea datos históricos de varios meses para probar evoluciones
    """
    hoy = date.today()
    escenarios = []
    
    for i in range(6):  # Últimos 6 meses
        mes = hoy.month - i
        año = hoy.year
        if mes <= 0:
            mes += 12
            año -= 1
        
        fecha_base = date(año, mes, 15)
        
        # Ingresos (van aumentando ligeramente)
        ingreso = Ingreso(
            usuario_id=usuario_base.id,
            cantidad=1500.00 + (i * 50),
            fecha=fecha_base,
            descripcion=f'Nómina {mes}/{año}',
            es_fijo=True
        )
        session.add(ingreso)
        
        # Gastos (variable)
        for cat in categorias_base[:3]:
            gasto = Gasto(
                usuario_id=usuario_base.id,
                categoria_id=cat.id,
                cantidad=random.uniform(100, 400) + (i * 10),
                fecha=fecha_base - timedelta(days=random.randint(1, 10)),
                descripcion=f'Gasto {cat.nombre} {mes}/{año}'
            )
            session.add(gasto)
        
        escenarios.append({
            'año': año,
            'mes': mes,
            'ingreso': 1500.00 + (i * 50)
        })
    
    session.commit()
    return escenarios
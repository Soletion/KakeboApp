"""
Pruebas de integración - Base de datos (Versión simplificada)
"""
import pytest
from sqlalchemy import inspect, func, extract
from app import db
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.categoria import Categoria
from app.models.gasto import Gasto
from app.models.ingreso import Ingreso
from app.models.objetivo_ahorro import ObjetivoAhorro
from datetime import date, timedelta
import random
import string

@pytest.mark.usefixtures('app_context')
class TestDatabaseIntegration:
    """Pruebas de integración de base de datos"""
    
    @pytest.fixture
    def usuario_test(self, session):
        """Crear usuario de prueba único"""
        sufijo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        rol = session.query(Rol).filter_by(nombre='usuario').first()
        assert rol is not None
        
        usuario = Usuario(
            username=f'dbtest_{sufijo}',
            email=f'dbtest_{sufijo}@example.com',
            nombre='DB',
            apellidos='Test',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        yield usuario
        
        # Limpiar después
        session.query(Gasto).filter_by(usuario_id=usuario.id).delete()
        session.query(Ingreso).filter_by(usuario_id=usuario.id).delete()
        session.query(ObjetivoAhorro).filter_by(usuario_id=usuario.id).delete()
        session.delete(usuario)
        session.commit()
    
    # =========================================================
    # VERIFICACIÓN DE ESTRUCTURA
    # =========================================================
    
    def test_tablas_existen(self):
        """Verificar que todas las tablas necesarias existen"""
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        tablas_requeridas = ['usuarios', 'roles', 'categorias', 'gastos', 'ingresos', 'objetivos_ahorro']
        
        for tabla in tablas_requeridas:
            assert tabla in tables, f"Tabla {tabla} no existe"
    
    def test_columnas_correctas(self):
        """Verificar que las tablas tienen las columnas correctas"""
        inspector = inspect(db.engine)
        
        # Verificar columnas de usuarios
        usuarios_columns = [c['name'] for c in inspector.get_columns('usuarios')]
        columnas_requeridas = ['id', 'email', 'username', 'password_hash', 'nombre', 'apellidos', 'rol_id', 'activo']
        for col in columnas_requeridas:
            assert col in usuarios_columns, f"Columna {col} no encontrada en usuarios"
        
        # Verificar columnas de gastos
        gastos_columns = [c['name'] for c in inspector.get_columns('gastos')]
        assert 'usuario_id' in gastos_columns
        assert 'categoria_id' in gastos_columns
        assert 'cantidad' in gastos_columns
        assert 'fecha' in gastos_columns
    
    # =========================================================
    # RELACIONES ENTRE TABLAS
    # =========================================================
    
    def test_relaciones_usuario_gastos(self, session, usuario_test):
        """Verificar relación Usuario - Gastos"""
        categoria = session.query(Categoria).first()
        
        gasto = Gasto(
            usuario_id=usuario_test.id,
            categoria_id=categoria.id,
            cantidad=100.00,
            fecha=date.today(),
            descripcion='Gasto prueba relación'
        )
        session.add(gasto)
        session.commit()
        
        # Verificar que existe al menos un gasto
        gastos_count = session.query(Gasto).filter_by(usuario_id=usuario_test.id).count()
        assert gastos_count >= 1
    
    def test_relaciones_usuario_ingresos(self, session, usuario_test):
        """Verificar relación Usuario - Ingresos"""
        ingreso = Ingreso(
            usuario_id=usuario_test.id,
            cantidad=1000.00,
            fecha=date.today(),
            descripcion='Ingreso prueba'
        )
        session.add(ingreso)
        session.commit()
        
        ingresos_count = session.query(Ingreso).filter_by(usuario_id=usuario_test.id).count()
        assert ingresos_count >= 1
    
    def test_relaciones_usuario_objetivos(self, session, usuario_test):
        """Verificar relación Usuario - ObjetivosAhorro"""
        objetivo = ObjetivoAhorro(
            usuario_id=usuario_test.id,
            nombre='Objetivo prueba',
            cantidad_objetivo=5000.00,
            fecha_inicio=date.today(),
            fecha_limite=date.today() + timedelta(days=365)
        )
        session.add(objetivo)
        session.commit()
        
        objetivos_count = session.query(ObjetivoAhorro).filter_by(usuario_id=usuario_test.id).count()
        assert objetivos_count >= 1
    
    def test_relacion_gasto_categoria(self, session, usuario_test):
        """Verificar relación Gasto - Categoría"""
        categoria = session.query(Categoria).first()
        
        gasto = Gasto(
            usuario_id=usuario_test.id,
            categoria_id=categoria.id,
            cantidad=50.00,
            fecha=date.today()
        )
        session.add(gasto)
        session.commit()
        
        # Verificar que la categoría existe
        assert gasto.categoria_id == categoria.id
    
    # =========================================================
    # INTEGRIDAD REFERENCIAL
    # =========================================================
    
    def test_cascada_eliminar_usuario(self, session, usuario_test):
        """Verificar que eliminar usuario elimina sus datos relacionados"""
        categoria = session.query(Categoria).first()
        
        # Crear datos relacionados
        gasto = Gasto(usuario_id=usuario_test.id, categoria_id=categoria.id, cantidad=100.00, fecha=date.today())
        ingreso = Ingreso(usuario_id=usuario_test.id, cantidad=2000.00, fecha=date.today())
        objetivo = ObjetivoAhorro(usuario_id=usuario_test.id, nombre='Test', cantidad_objetivo=1000.00, fecha_inicio=date.today())
        
        session.add_all([gasto, ingreso, objetivo])
        session.commit()
        
        # Contar registros relacionados
        gastos_count = session.query(Gasto).filter_by(usuario_id=usuario_test.id).count()
        assert gastos_count >= 1
        
        # Eliminar usuario
        session.delete(usuario_test)
        session.commit()
        
        # Verificar que los registros relacionados desaparecieron
        gastos_post = session.query(Gasto).filter_by(usuario_id=usuario_test.id).count()
        assert gastos_post == 0
    
    # =========================================================
    # CONSULTAS COMPLEJAS
    # =========================================================
    
    def test_consulta_compleja_gastos_por_mes(self, session, usuario_test):
        """Verificar consulta de gastos agrupados por mes"""
        categoria = session.query(Categoria).first()
        
        # Crear gastos en diferentes meses
        gasto1 = Gasto(usuario_id=usuario_test.id, categoria_id=categoria.id, cantidad=100.00, fecha=date(2024, 1, 15))
        gasto2 = Gasto(usuario_id=usuario_test.id, categoria_id=categoria.id, cantidad=200.00, fecha=date(2024, 2, 20))
        
        session.add_all([gasto1, gasto2])
        session.commit()
        
        # Consulta de gastos por mes
        resultados = session.query(
            extract('year', Gasto.fecha).label('año'),
            extract('month', Gasto.fecha).label('mes'),
            func.sum(Gasto.cantidad).label('total')
        ).filter_by(usuario_id=usuario_test.id).group_by('año', 'mes').all()
        
        assert len(resultados) >= 2
    
    def test_consulta_compleja_comparativa_ingresos_gastos(self, session, usuario_test):
        """Verificar consulta comparativa ingresos vs gastos"""
        categoria = session.query(Categoria).first()
        
        # Crear gastos e ingresos
        gasto = Gasto(usuario_id=usuario_test.id, categoria_id=categoria.id, cantidad=300.00, fecha=date(2024, 3, 15))
        ingreso = Ingreso(usuario_id=usuario_test.id, cantidad=1000.00, fecha=date(2024, 3, 15))
        
        session.add_all([gasto, ingreso])
        session.commit()
        
        # Consulta que suma gastos e ingresos del mismo mes
        gastos_mes = session.query(func.sum(Gasto.cantidad)).filter_by(usuario_id=usuario_test.id).scalar() or 0
        ingresos_mes = session.query(func.sum(Ingreso.cantidad)).filter_by(usuario_id=usuario_test.id).scalar() or 0
        
        balance = ingresos_mes - gastos_mes
        assert balance == 700.00
    
    # =========================================================
    # TRANSACCIONES
    # =========================================================
    
    def test_transaccion_atomica(self, session, usuario_test):
        """Verificar atomicidad de transacciones"""
        categoria = session.query(Categoria).first()
        
        # Contar gastos antes
        count_before = session.query(Gasto).filter_by(usuario_id=usuario_test.id).count()
        
        # Intentar crear gasto con datos inválidos
        try:
            gasto1 = Gasto(usuario_id=usuario_test.id, categoria_id=categoria.id, cantidad=100.00, fecha=date.today())
            gasto2 = Gasto(usuario_id=usuario_test.id, categoria_id=99999, cantidad=200.00, fecha=date.today())
            
            session.add_all([gasto1, gasto2])
            session.commit()
        except Exception:
            session.rollback()
        
        # Verificar que no se guardó ningún gasto
        count_after = session.query(Gasto).filter_by(usuario_id=usuario_test.id).count()
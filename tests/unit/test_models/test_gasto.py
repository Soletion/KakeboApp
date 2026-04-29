"""
Tests unitarios para el modelo Gasto
"""
import pytest
from app.models.gasto import Gasto
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.rol import Rol
from app.extensions import db
from datetime import datetime, date, timedelta
import time

@pytest.mark.usefixtures('app_context')
class TestGastoModel:
    """Pruebas para el modelo Gasto"""
    
    @pytest.fixture(autouse=True)
    def crear_usuario_unico(self, session):
        """Crea un usuario único para cada prueba"""
        import random
        import string
        
        # Generar username y email únicos
        sufijo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        rol = Rol.query.filter_by(nombre='usuario').first()
        assert rol is not None
        
        usuario = Usuario(
            username=f'testuser_{sufijo}',
            email=f'test_{sufijo}@example.com',
            nombre='Test',
            apellidos='Usuario',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        
        session.add(usuario)
        session.commit()
        
        self.usuario = usuario
        yield
        # No es necesario limpiar porque la transacción se revierte
    
    def test_crear_gasto_valido(self, session):
        """Test: Crear gasto con datos válidos"""
        categoria = Categoria.query.first()
        assert categoria is not None
        
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=50.00,
            fecha=date.today(),
            descripcion='Compra de prueba'
        )
        
        session.add(gasto)
        session.commit()
        
        assert gasto.id is not None
        assert gasto.usuario_id == self.usuario.id
        assert gasto.categoria_id == categoria.id
        assert float(gasto.cantidad) == 50.00
        assert gasto.descripcion == 'Compra de prueba'
        assert gasto.fecha_registro is not None
    
    def test_cantidad_negativa(self, session):
        """Test: No se permite cantidad negativa"""
        categoria = Categoria.query.first()
        
        with pytest.raises(ValueError, match="mayor a 0"):
            gasto = Gasto(
                usuario_id=self.usuario.id,
                categoria_id=categoria.id,
                cantidad=-10.00,
                fecha=date.today()
            )
    
    def test_cantidad_cero(self, session):
        """Test: No se permite cantidad cero"""
        categoria = Categoria.query.first()
        
        with pytest.raises(ValueError, match="mayor a 0"):
            gasto = Gasto(
                usuario_id=self.usuario.id,
                categoria_id=categoria.id,
                cantidad=0,
                fecha=date.today()
            )
    
    def test_fecha_futura(self, session):
        """Test: No se permite fecha futura"""
        categoria = Categoria.query.first()
        fecha_futura = date.today() + timedelta(days=1)
        
        with pytest.raises(ValueError, match="fecha no puede ser futura"):
            gasto = Gasto(
                usuario_id=self.usuario.id,
                categoria_id=categoria.id,
                cantidad=50.00,
                fecha=fecha_futura
            )
    
    def test_propiedad_mes(self, session):
        """Test: Propiedad mes devuelve YYYY-MM"""
        categoria = Categoria.query.first()
        
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=50.00,
            fecha=date(2024, 3, 15)
        )
        
        assert gasto.mes == '2024-03'
    
    def test_obtener_por_usuario_y_mes(self, session):
        """Test: Obtener gastos por usuario y mes"""
        categoria = Categoria.query.first()
        
        # Crear un gasto de prueba
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=25.00,
            fecha=date.today()
        )
        session.add(gasto)
        session.commit()
        
        año = date.today().year
        mes = date.today().month
        
        gastos = Gasto.obtener_por_usuario_y_mes(self.usuario.id, año, mes)
        
        assert isinstance(gastos, list)
        assert len(gastos) >= 1
        for g in gastos:
            assert g.usuario_id == self.usuario.id
            assert g.fecha.year == año
            assert g.fecha.month == mes
    
    def test_obtener_por_categoria_y_mes(self, session):
        """Test: Obtener gastos filtrados por categoría"""
        categoria = Categoria.query.first()
        
        # Crear un gasto de prueba
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=25.00,
            fecha=date.today()
        )
        session.add(gasto)
        session.commit()
        
        año = date.today().year
        mes = date.today().month
        
        gastos = Gasto.obtener_por_categoria_y_mes(
            self.usuario.id, 
            categoria.id, 
            año, 
            mes
        )
        
        assert isinstance(gastos, list)
        assert len(gastos) >= 1
        for g in gastos:
            assert g.categoria_id == categoria.id
    
    def test_total_mes(self, session):
        """Test: Calcular total de gastos del mes"""
        categoria = Categoria.query.first()
        
        # Crear un gasto
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=100.00,
            fecha=date.today()
        )
        session.add(gasto)
        session.commit()
        
        año = date.today().year
        mes = date.today().month
        
        total = Gasto.total_mes(self.usuario.id, año, mes)
        
        assert isinstance(total, float)
        assert total >= 100.00
    
    def test_total_por_categoria_mes(self, session):
        """Test: Calcular totales por categoría del mes"""
        categoria = Categoria.query.first()
        
        # Crear un gasto
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=50.00,
            fecha=date.today()
        )
        session.add(gasto)
        session.commit()
        
        año = date.today().year
        mes = date.today().month
        
        totales = Gasto.total_por_categoria_mes(self.usuario.id, año, mes)
        
        assert isinstance(totales, dict)
        assert categoria.id in totales
        assert totales[categoria.id] >= 50.00
    
    def test_obtener_ultimos(self, session):
        """Test: Obtener últimos gastos"""
        categoria = Categoria.query.first()
        
        # Crear algunos gastos
        for i in range(3):
            gasto = Gasto(
                usuario_id=self.usuario.id,
                categoria_id=categoria.id,
                cantidad=10.00 + i,
                fecha=date.today() - timedelta(days=i)
            )
            session.add(gasto)
        session.commit()
        
        limite = 5
        gastos = Gasto.obtener_ultimos(self.usuario.id, limite)
        
        assert len(gastos) <= limite
        assert len(gastos) >= 3
        if len(gastos) > 1:
            # Verificar orden descendente
            for i in range(len(gastos) - 1):
                assert gastos[i].fecha >= gastos[i+1].fecha
    
    def test_busqueda_avanzada(self, session):
        """Test: Búsqueda avanzada con múltiples filtros"""
        categoria = Categoria.query.first()
        
        # Crear gasto de prueba
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=50.00,
            fecha=date.today(),
            descripcion='Compra para test'
        )
        session.add(gasto)
        session.commit()
        
        fecha_desde = date.today() - timedelta(days=30)
        filtros = {
            'fecha_desde': fecha_desde,
            'cantidad_min': 10
        }
        
        resultados = Gasto.buscar(self.usuario.id, **filtros)
        
        assert isinstance(resultados, list)
        assert len(resultados) >= 1
        for g in resultados:
            assert g.fecha >= fecha_desde
            assert float(g.cantidad) >= 10
    
    def test_busqueda_por_descripcion(self, session):
        """Test: Búsqueda por texto en descripción"""
        categoria = Categoria.query.first()
        
        # Crear gasto con descripción específica
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=30.00,
            fecha=date.today(),
            descripcion='Texto especial de prueba'
        )
        session.add(gasto)
        session.commit()
        
        filtros = {'descripcion': 'especial'}
        resultados = Gasto.buscar(self.usuario.id, **filtros)
        
        assert isinstance(resultados, list)
        assert len(resultados) >= 1
    
    def test_to_dict(self, session):
        """Test: Conversión a diccionario"""
        categoria = Categoria.query.first()
        
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=75.50,
            fecha=date.today(),
            descripcion='Test dict'
        )
        
        session.add(gasto)
        session.commit()
        
        data = gasto.to_dict()
        
        assert data['id'] == gasto.id
        assert data['usuario_id'] == self.usuario.id
        assert data['categoria_id'] == categoria.id
        assert data['cantidad'] == 75.50
        assert data['descripcion'] == 'Test dict'
        assert 'fecha' in data
        assert 'mes' in data
    
    def test_repr(self, session):
        """Test: Representación string"""
        categoria = Categoria.query.first()
        
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=25.00,
            fecha=date.today()
        )
        
        repr_str = repr(gasto)
        assert '25' in repr_str
        assert str(date.today()) in repr_str
    
    def test_actualizado_automatico(self, session):
        """Test: El campo actualizado se modifica automáticamente"""
        categoria = Categoria.query.first()
        
        gasto = Gasto(
            usuario_id=self.usuario.id,
            categoria_id=categoria.id,
            cantidad=30.00,
            fecha=date.today()
        )
        session.add(gasto)
        session.commit()
        
        fecha_actualizado_original = gasto.actualizado
        
        # Esperar un momento para asegurar diferencia
        time.sleep(0.1)
        
        # Modificar y guardar
        gasto.cantidad = 35.00
        session.commit()
        
        # El campo actualizado debería haber cambiado
        assert gasto.actualizado > fecha_actualizado_original
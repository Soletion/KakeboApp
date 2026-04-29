"""
Tests unitarios para el modelo Ingreso
"""
import pytest
from app.models.ingreso import Ingreso
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.extensions import db
from datetime import datetime, date, timedelta
import time
import random
import string

@pytest.mark.usefixtures('app_context')
class TestIngresoModel:
    """Pruebas para el modelo Ingreso"""
    
    @pytest.fixture(autouse=True)
    def crear_usuario_unico(self, session):
        """Crea un usuario único para cada prueba"""
        # Generar username y email únicos
        sufijo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        rol = Rol.query.filter_by(nombre='usuario').first()
        assert rol is not None
        
        usuario = Usuario(
            username=f'testingreso_{sufijo}',
            email=f'ingreso_{sufijo}@example.com',
            nombre='Test',
            apellidos='Ingreso',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        
        session.add(usuario)
        session.commit()
        
        self.usuario = usuario
        yield
    
    def test_crear_ingreso_valido(self, session):
        """Test: Crear ingreso con datos válidos"""
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=2500.00,
            fecha=date.today(),
            descripcion='Salario mensual',
            es_fijo=True
        )
        
        session.add(ingreso)
        session.commit()
        
        assert ingreso.id is not None
        assert ingreso.usuario_id == self.usuario.id
        assert float(ingreso.cantidad) == 2500.00
        assert ingreso.descripcion == 'Salario mensual'
        assert ingreso.es_fijo is True
        assert ingreso.fecha_registro is not None
    
    def test_cantidad_negativa(self, session):
        """Test: No se permite cantidad negativa"""
        with pytest.raises(ValueError, match="mayor a 0"):
            ingreso = Ingreso(
                usuario_id=self.usuario.id,
                cantidad=-100.00,
                fecha=date.today()
            )
    
    def test_cantidad_cero(self, session):
        """Test: No se permite cantidad cero"""
        with pytest.raises(ValueError, match="mayor a 0"):
            ingreso = Ingreso(
                usuario_id=self.usuario.id,
                cantidad=0,
                fecha=date.today()
            )
    
    def test_fecha_futura(self, session):
        """Test: No se permite fecha futura"""
        fecha_futura = date.today() + timedelta(days=1)
        
        with pytest.raises(ValueError, match="fecha no puede ser futura"):
            ingreso = Ingreso(
                usuario_id=self.usuario.id,
                cantidad=1000.00,
                fecha=fecha_futura
            )
    
    def test_propiedad_mes(self, session):
        """Test: Propiedad mes devuelve YYYY-MM"""
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=1000.00,
            fecha=date(2024, 5, 20)
        )
        
        assert ingreso.mes == '2024-05'
    
    def test_obtener_por_usuario_y_mes(self, session):
        """Test: Obtener ingresos por usuario y mes"""
        # Crear ingreso de prueba
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=1500.00,
            fecha=date.today(),
            descripcion='Ingreso prueba'
        )
        session.add(ingreso)
        session.commit()
        
        año = date.today().year
        mes = date.today().month
        
        ingresos = Ingreso.obtener_por_usuario_y_mes(self.usuario.id, año, mes)
        
        assert isinstance(ingresos, list)
        assert len(ingresos) >= 1
        for ing in ingresos:
            assert ing.usuario_id == self.usuario.id
            assert ing.fecha.year == año
            assert ing.fecha.month == mes
    
    def test_total_mes(self, session):
        """Test: Calcular total de ingresos del mes"""
        # Crear algunos ingresos
        montos = [1000.00, 500.00, 200.00]
        for monto in montos:
            ingreso = Ingreso(
                usuario_id=self.usuario.id,
                cantidad=monto,
                fecha=date.today()
            )
            session.add(ingreso)
        session.commit()
        
        año = date.today().year
        mes = date.today().month
        
        total = Ingreso.total_mes(self.usuario.id, año, mes)
        
        assert isinstance(total, float)
        assert total == sum(montos)
    
    def test_ingresos_fijos_mes(self, session):
        """Test: Obtener solo ingresos fijos del mes"""
        # Crear ingresos fijos
        ingreso_fijo = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=2000.00,
            fecha=date.today(),
            es_fijo=True,
            descripcion='Nómina'
        )
        session.add(ingreso_fijo)
        
        # Crear ingreso variable
        ingreso_variable = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=300.00,
            fecha=date.today(),
            es_fijo=False,
            descripcion='Freelance'
        )
        session.add(ingreso_variable)
        session.commit()
        
        año = date.today().year
        mes = date.today().month
        
        fijos = Ingreso.ingresos_fijos_mes(self.usuario.id, año, mes)
        
        assert isinstance(fijos, list)
        assert len(fijos) >= 1
        for ing in fijos:
            assert ing.es_fijo is True
    
    def test_ingresos_variables_mes(self, session):
        """Test: Obtener solo ingresos variables del mes"""
        # Crear ingreso fijo
        ingreso_fijo = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=2000.00,
            fecha=date.today(),
            es_fijo=True
        )
        session.add(ingreso_fijo)
        
        # Crear ingresos variables
        ingreso_variable1 = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=300.00,
            fecha=date.today(),
            es_fijo=False
        )
        ingreso_variable2 = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=150.00,
            fecha=date.today(),
            es_fijo=False
        )
        session.add(ingreso_variable1)
        session.add(ingreso_variable2)
        session.commit()
        
        año = date.today().year
        mes = date.today().month
        
        variables = Ingreso.ingresos_variables_mes(self.usuario.id, año, mes)
        
        assert isinstance(variables, list)
        assert len(variables) >= 2
        for ing in variables:
            assert ing.es_fijo is False
    
    def test_total_ingresos_fijos(self, session):
        """Test: Calcular total de ingresos fijos"""
        # Crear ingresos fijos
        montos_fijos = [2000.00, 500.00]
        for monto in montos_fijos:
            ingreso = Ingreso(
                usuario_id=self.usuario.id,
                cantidad=monto,
                fecha=date.today(),
                es_fijo=True
            )
            session.add(ingreso)
        session.commit()
        
        total = Ingreso.total_ingresos_fijos(self.usuario.id)
        
        assert isinstance(total, float)
        assert total == sum(montos_fijos)
    
    def test_obtener_ultimos(self, session):
        """Test: Obtener últimos ingresos"""
        # Crear varios ingresos con diferentes fechas
        for i in range(3):
            ingreso = Ingreso(
                usuario_id=self.usuario.id,
                cantidad=1000.00 + (i * 100),
                fecha=date.today() - timedelta(days=i)
            )
            session.add(ingreso)
        session.commit()
        
        limite = 5
        ingresos = Ingreso.obtener_ultimos(self.usuario.id, limite)
        
        assert isinstance(ingresos, list)
        assert len(ingresos) <= limite
        assert len(ingresos) >= 3
        
        if len(ingresos) > 1:
            # Verificar orden descendente (fechas más recientes primero)
            for i in range(len(ingresos) - 1):
                assert ingresos[i].fecha >= ingresos[i+1].fecha
    
    def test_busqueda_avanzada(self, session):
        """Test: Búsqueda avanzada con múltiples filtros"""
        # Crear ingreso de prueba
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=2500.00,
            fecha=date.today(),
            descripcion='Ingreso principal',
            es_fijo=True
        )
        session.add(ingreso)
        session.commit()
        
        fecha_desde = date.today() - timedelta(days=30)
        filtros = {
            'fecha_desde': fecha_desde,
            'cantidad_min': 1000,
            'es_fijo': True
        }
        
        resultados = Ingreso.buscar(self.usuario.id, **filtros)
        
        assert isinstance(resultados, list)
        assert len(resultados) >= 1
        for ing in resultados:
            assert ing.fecha >= fecha_desde
            assert float(ing.cantidad) >= 1000
            assert ing.es_fijo is True
    
    def test_busqueda_por_descripcion(self, session):
        """Test: Búsqueda por texto en descripción"""
        # Crear ingreso con descripción específica
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=500.00,
            fecha=date.today(),
            descripcion='Bono especial de fin de año'
        )
        session.add(ingreso)
        session.commit()
        
        filtros = {'descripcion': 'especial'}
        resultados = Ingreso.buscar(self.usuario.id, **filtros)
        
        assert isinstance(resultados, list)
        assert len(resultados) >= 1
        for ing in resultados:
            assert 'especial' in ing.descripcion.lower()
    
    def test_to_dict(self, session):
        """Test: Conversión a diccionario"""
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=1800.50,
            fecha=date.today(),
            descripcion='Test diccionario',
            es_fijo=True
        )
        
        session.add(ingreso)
        session.commit()
        
        data = ingreso.to_dict()
        
        assert data['id'] == ingreso.id
        assert data['usuario_id'] == self.usuario.id
        assert data['cantidad'] == 1800.50
        assert data['descripcion'] == 'Test diccionario'
        assert data['es_fijo'] is True
        assert 'fecha' in data
        assert 'mes' in data
    
    def test_repr(self, session):
        """Test: Representación string"""
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=750.00,
            fecha=date.today()
        )
        
        repr_str = repr(ingreso)
        assert '750' in repr_str or '750.0' in repr_str
        assert str(date.today()) in repr_str
    
    def test_actualizado_automatico(self, session):
        """Test: El campo actualizado se modifica automáticamente"""
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=3000.00,
            fecha=date.today()
        )
        session.add(ingreso)
        session.commit()
        
        fecha_actualizado_original = ingreso.actualizado
        
        # Esperar un momento
        time.sleep(0.1)
        
        # Modificar y guardar
        ingreso.cantidad = 3500.00
        session.commit()
        
        # El campo actualizado debería haber cambiado
        assert ingreso.actualizado > fecha_actualizado_original
    
    def test_ingreso_sin_descripcion(self, session):
        """Test: Crear ingreso sin descripción (debería ser None)"""
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=1000.00,
            fecha=date.today()
        )
        
        session.add(ingreso)
        session.commit()
        
        assert ingreso.id is not None
        assert ingreso.descripcion is None
    
    def test_ingreso_es_fijo_default(self, session):
        """Test: Valor por defecto de es_fijo debe ser False"""
        ingreso = Ingreso(
            usuario_id=self.usuario.id,
            cantidad=1000.00,
            fecha=date.today()
        )
        
        session.add(ingreso)
        session.commit()
        
        assert ingreso.es_fijo is False
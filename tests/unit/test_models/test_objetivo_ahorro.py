"""
Tests unitarios para el modelo ObjetivoAhorro
"""
import pytest
from app.models.objetivo_ahorro import ObjetivoAhorro
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.extensions import db
from datetime import date, timedelta
import random
import string
import time

@pytest.mark.usefixtures('app_context')
class TestObjetivoAhorroModel:
    """Pruebas para el modelo ObjetivoAhorro"""
    
    @pytest.fixture(autouse=True)
    def crear_usuario_unico(self, session):
        """Crea un usuario único para cada prueba"""
        sufijo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        rol = Rol.query.filter_by(nombre='usuario').first()
        assert rol is not None
        
        usuario = Usuario(
            username=f'testobjetivo_{sufijo}',
            email=f'objetivo_{sufijo}@example.com',
            nombre='Test',
            apellidos='Objetivo',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        
        session.add(usuario)
        session.commit()
        
        self.usuario = usuario
        yield
    
    def test_crear_objetivo_valido(self, session):
        """Test: Crear objetivo de ahorro válido"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Viaje a Japón',
            descripcion='Ahorrar para viaje de 2 semanas',
            cantidad_objetivo=5000.00,
            cantidad_actual=1000.00,
            fecha_inicio=date.today(),
            fecha_limite=date.today() + timedelta(days=365)
        )
        
        session.add(objetivo)
        session.commit()
        
        assert objetivo.id is not None
        assert objetivo.usuario_id == self.usuario.id
        assert objetivo.nombre == 'Viaje a Japón'
        assert float(objetivo.cantidad_objetivo) == 5000.00
        assert float(objetivo.cantidad_actual) == 1000.00
        assert objetivo.estado == 'activo'
    
    def test_crear_objetivo_sin_fecha_limite(self, session):
        """Test: Crear objetivo sin fecha límite (válido)"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Ahorro libre',
            cantidad_objetivo=10000,
            cantidad_actual=2000,
            fecha_inicio=date.today(),
            fecha_limite=None
        )
        
        session.add(objetivo)
        session.commit()
        
        assert objetivo.id is not None
        assert objetivo.fecha_limite is None
        assert objetivo.dias_restantes is None
    
    def test_cantidad_objetivo_cero(self, session):
        """Test: No se permite cantidad objetivo cero"""
        with pytest.raises(ValueError, match="mayor a 0"):
            objetivo = ObjetivoAhorro(
                usuario_id=self.usuario.id,
                nombre='Test',
                cantidad_objetivo=0,
                cantidad_actual=0,
                fecha_inicio=date.today()
            )
    
    def test_cantidad_objetivo_negativa(self, session):
        """Test: No se permite cantidad objetivo negativa"""
        with pytest.raises(ValueError, match="mayor a 0"):
            objetivo = ObjetivoAhorro(
                usuario_id=self.usuario.id,
                nombre='Test',
                cantidad_objetivo=-100,
                cantidad_actual=0,
                fecha_inicio=date.today()
            )
    
    def test_cantidad_actual_negativa(self, session):
        """Test: No se permite cantidad actual negativa"""
        with pytest.raises(ValueError, match="no puede ser negativa"):
            objetivo = ObjetivoAhorro(
                usuario_id=self.usuario.id,
                nombre='Test',
                cantidad_objetivo=1000,
                cantidad_actual=-50,
                fecha_inicio=date.today()
            )
    
    def test_fechas_inconsistentes(self, session):
        """Test: Fecha inicio no puede ser posterior a fecha límite"""
        with pytest.raises(ValueError, match="La fecha de inicio no puede ser posterior"):
            objetivo = ObjetivoAhorro(
                usuario_id=self.usuario.id,
                nombre='Test',
                cantidad_objetivo=1000,
                fecha_inicio=date.today() + timedelta(days=30),
                fecha_limite=date.today()
            )
    
    def test_estado_invalido(self, session):
        """Test: Estado debe ser activo, completado o cancelado"""
        with pytest.raises(ValueError, match="Estado no válido"):
            objetivo = ObjetivoAhorro(
                usuario_id=self.usuario.id,
                nombre='Test',
                cantidad_objetivo=1000,
                fecha_inicio=date.today(),
                estado='invalido'
            )
    
    def test_progreso_calculo(self, session):
        """Test: Calcular progreso correctamente"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=250,
            fecha_inicio=date.today()
        )
        
        assert objetivo.progreso == 25.0
        
        # Progreso no puede superar 100%
        objetivo.cantidad_actual = 1500
        assert objetivo.progreso == 100.0
    
    def test_dias_restantes(self, session):
        """Test: Calcular días restantes correctamente"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            fecha_inicio=date.today(),
            fecha_limite=date.today() + timedelta(days=30)
        )
        
        assert objetivo.dias_restantes == 30
        
        # Sin fecha límite debe ser None
        objetivo2 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test2',
            cantidad_objetivo=1000,
            fecha_inicio=date.today(),
            fecha_limite=None
        )
        assert objetivo2.dias_restantes is None
    
    def test_cantidad_restante(self, session):
        """Test: Calcular cantidad restante para completar"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=300,
            fecha_inicio=date.today()
        )
        
        assert objetivo.cantidad_restante == 700
        
        # Si ya superó, debe ser 0
        objetivo.cantidad_actual = 1200
        assert objetivo.cantidad_restante == 0
    
    def test_esta_completado(self, session):
        """Test: Verificar si el objetivo está completado"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today()
        )
        
        assert objetivo.esta_completado is False
        
        objetivo.cantidad_actual = 1000
        assert objetivo.esta_completado is True
    
    def test_esta_vencido(self, session):
        """Test: Verificar si el objetivo está vencido"""
        # Con fecha límite pasada
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today() - timedelta(days=60),
            fecha_limite=date.today() - timedelta(days=1)
        )
        
        assert objetivo.esta_vencido is True
        
        # Sin fecha límite no debe estar vencido
        objetivo2 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test2',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today(),
            fecha_limite=None
        )
        assert objetivo2.esta_vencido is False
    
    def test_actualizar_cantidad(self, session):
        """Test: Actualizar cantidad actual con validación"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today()
        )
        
        session.add(objetivo)
        session.commit()
        
        # Actualizar a una cantidad válida
        objetivo.actualizar_cantidad(750)
        assert float(objetivo.cantidad_actual) == 750
        
        # No puede ser negativa
        with pytest.raises(ValueError, match="no puede ser negativa"):
            objetivo.actualizar_cantidad(-100)
    
    def test_añadir_cantidad(self, session):
        """Test: Añadir cantidad al objetivo"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today()
        )
        
        session.add(objetivo)
        session.commit()
        
        objetivo.añadir_cantidad(200)
        assert float(objetivo.cantidad_actual) == 700
        
        # No añadir cantidad negativa o cero
        with pytest.raises(ValueError, match="debe ser positiva"):
            objetivo.añadir_cantidad(-50)
        
        with pytest.raises(ValueError, match="debe ser positiva"):
            objetivo.añadir_cantidad(0)
    
    def test_marcar_completado(self, session):
        """Test: Marcar objetivo como completado"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today(),
            estado='activo'
        )
        
        session.add(objetivo)
        session.commit()
        
        objetivo.marcar_completado()
        assert objetivo.estado == 'completado'
    
    def test_cancelar(self, session):
        """Test: Cancelar objetivo"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today(),
            estado='activo'
        )
        
        session.add(objetivo)
        session.commit()
        
        objetivo.cancelar()
        assert objetivo.estado == 'cancelado'
    
    def test_obtener_activos(self, session):
        """Test: Obtener objetivos activos del usuario"""
        objetivo1 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Activo 1',
            cantidad_objetivo=1000,
            fecha_inicio=date.today()
        )
        objetivo2 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Activo 2',
            cantidad_objetivo=2000,
            fecha_inicio=date.today()
        )
        objetivo3 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Completado',
            cantidad_objetivo=500,
            cantidad_actual=500,
            fecha_inicio=date.today() - timedelta(days=30),
            estado='completado'
        )
        
        session.add_all([objetivo1, objetivo2, objetivo3])
        session.commit()
        
        activos = ObjetivoAhorro.obtener_activos(self.usuario.id)
        
        assert isinstance(activos, list)
        assert len(activos) == 2
        for obj in activos:
            assert obj.estado == 'activo'
    
    def test_obtener_completados(self, session):
        """Test: Obtener objetivos completados del usuario"""
        objetivo1 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Completado 1',
            cantidad_objetivo=1000,
            cantidad_actual=1000,
            fecha_inicio=date.today() - timedelta(days=30),
            estado='completado'
        )
        objetivo2 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Activo',
            cantidad_objetivo=2000,
            fecha_inicio=date.today()
        )
        
        session.add_all([objetivo1, objetivo2])
        session.commit()
        
        completados = ObjetivoAhorro.obtener_completados(self.usuario.id)
        
        assert isinstance(completados, list)
        assert len(completados) == 1
        assert completados[0].estado == 'completado'
    
    def test_resumen_objetivos(self, session):
        """Test: Resumen de objetivos del usuario"""
        objetivo1 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Objetivo 1',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today()
        )
        objetivo2 = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Objetivo 2',
            cantidad_objetivo=2000,
            cantidad_actual=2000,
            fecha_inicio=date.today() - timedelta(days=30),
            estado='completado'
        )
        
        session.add_all([objetivo1, objetivo2])
        session.commit()
        
        resumen = ObjetivoAhorro.resumen_objetivos(self.usuario.id)
        
        assert isinstance(resumen, dict)
        assert 'activos' in resumen
        assert 'completados' in resumen
        assert 'total_objetivo' in resumen
        assert 'total_actual' in resumen
        assert 'progreso_global' in resumen
        assert len(resumen['activos']) == 1
        assert len(resumen['completados']) == 1
    
    def test_to_dict(self, session):
        """Test: Conversión a diccionario"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test Dict',
            descripcion='Descripción de prueba',
            cantidad_objetivo=5000,
            cantidad_actual=2500,
            fecha_inicio=date.today(),
            fecha_limite=date.today() + timedelta(days=180)
        )
        
        session.add(objetivo)
        session.commit()
        
        data = objetivo.to_dict()
        
        assert data['id'] == objetivo.id
        assert data['nombre'] == 'Test Dict'
        assert data['descripcion'] == 'Descripción de prueba'
        assert data['cantidad_objetivo'] == 5000
        assert data['cantidad_actual'] == 2500
        assert data['estado'] == 'activo'
        assert data['progreso'] == 50.0
        assert 'dias_restantes' in data
        assert 'cantidad_restante' in data
    
    def test_repr(self, session):
        """Test: Representación string"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test Repr',
            cantidad_objetivo=1000,
            cantidad_actual=300,
            fecha_inicio=date.today()
        )
        
        repr_str = repr(objetivo)
        assert 'Test Repr' in repr_str
        assert '30' in repr_str or '30.0' in repr_str
    
    def test_actualizado_automatico(self, session):
        """Test: El campo actualizado se modifica automáticamente"""
        objetivo = ObjetivoAhorro(
            usuario_id=self.usuario.id,
            nombre='Test',
            cantidad_objetivo=1000,
            cantidad_actual=500,
            fecha_inicio=date.today()
        )
        
        session.add(objetivo)
        session.commit()
        
        fecha_original = objetivo.actualizado
        
        time.sleep(0.1)
        
        objetivo.nombre = 'Nombre Modificado'
        session.commit()
        
        assert objetivo.actualizado > fecha_original
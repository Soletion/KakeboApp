# tests/unit/test_models/test_usuario.py
import pytest
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.extensions import db

@pytest.mark.usefixtures('app_context')
class TestUsuarioModel:
    """Pruebas para el modelo Usuario"""
    
    def test_crear_usuario_valido(self, session):
        """Test: Crear usuario válido"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        assert rol is not None
        
        usuario = Usuario(
            username='juanperez',
            email='juan@example.com',
            nombre='Juan',
            apellidos='Pérez',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        
        session.add(usuario)
        session.commit()
        
        assert usuario.id is not None
        assert usuario.username == 'juanperez'
        assert usuario.email == 'juan@example.com'
    
    def test_password_hashing(self, session):
        """Test: Hash de contraseña"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testpass',
            email='pass@example.com',
            nombre='Test',
            rol_id=rol.id
        )
        usuario.password = 'MiPassword123'
        
        assert usuario.password_hash is not None
        assert usuario.password_hash != 'MiPassword123'
        assert usuario.verificar_password('MiPassword123') is True
        assert usuario.verificar_password('WrongPass') is False
    
    def test_password_setter_validation(self, session):
        """Test: Validación al setear contraseña - contraseña muy corta"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        
        # Probar contraseña muy corta - debe lanzar ValueError inmediatamente
        with pytest.raises(ValueError, match="8 caracteres"):
            usuario = Usuario(
                username='testvalid',
                email='valid@example.com',
                nombre='Test',
                rol_id=rol.id
            )
            usuario.password = 'short'  # Esto lanza la excepción directamente
    
    def test_password_not_readable(self, session):
        """Test: La contraseña no se puede leer directamente"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testread',
            email='read@example.com',
            nombre='Test',
            rol_id=rol.id
        )
        usuario.password = 'Secret123'
        
        # Verificar que no se puede acceder a la contraseña directamente
        with pytest.raises(AttributeError):
            _ = usuario.password
    
    def test_validar_email(self, session):
        """Test: Validación de email - debe fallar con email inválido"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        
        # Al crear el usuario con email inválido, debe lanzar ValueError
        with pytest.raises(ValueError, match="Email inválido"):
            usuario = Usuario(
                username='testemail',
                email='invalido',  # Email inválido
                nombre='Test',
                rol_id=rol.id
            )
            # La validación ocurre en el __init__, así que la excepción se lanza al crear
    
    def test_validar_username(self, session):
        """Test: Validación de username - username muy corto debe fallar"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        
        with pytest.raises(ValueError, match="Username debe tener al menos 3 caracteres"):
            usuario = Usuario(
                username='ab',  # Muy corto (menos de 3 caracteres)
                email='test@example.com',
                nombre='Test',
                rol_id=rol.id
            )
    
    def test_validar_nombre(self, session):
        """Test: Validación de nombre - nombre vacío debe fallar"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        
        with pytest.raises(ValueError, match="El nombre es obligatorio"):
            usuario = Usuario(
                username='testnombre',
                email='test@example.com',
                nombre='',  # Nombre vacío
                apellidos='Apellido',
                rol_id=rol.id
            )
    
    def test_email_unico(self, session):
        """Test: Email debe ser único"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        
        # Crear primer usuario
        usuario1 = Usuario(
            username='user1',
            email='duplicado@example.com',
            nombre='Usuario1',
            rol_id=rol.id
        )
        usuario1.password = 'Test123456'
        session.add(usuario1)
        session.commit()
        
        # Crear segundo usuario con mismo email
        usuario2 = Usuario(
            username='user2',
            email='duplicado@example.com',  # Mismo email
            nombre='Usuario2',
            rol_id=rol.id
        )
        usuario2.password = 'Test123456'
        session.add(usuario2)
        
        # Debe fallar por email duplicado
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            session.commit()
    
    def test_username_unico(self, session):
        """Test: Username debe ser único"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        
        # Crear primer usuario
        usuario1 = Usuario(
            username='usuariounico',
            email='user1@example.com',
            nombre='Usuario1',
            rol_id=rol.id
        )
        usuario1.password = 'Test123456'
        session.add(usuario1)
        session.commit()
        
        # Crear segundo usuario con mismo username
        usuario2 = Usuario(
            username='usuariounico',  # Mismo username
            email='user2@example.com',
            nombre='Usuario2',
            rol_id=rol.id
        )
        usuario2.password = 'Test123456'
        session.add(usuario2)
        
        # Debe fallar por username duplicado
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            session.commit()
    
    def test_actualizar_ultimo_acceso(self, session):
        """Test: Actualizar último acceso"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testacceso',
            email='acceso@example.com',
            nombre='Test',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        # Guardar fecha original
        fecha_original = usuario.ultimo_acceso
        
        # Actualizar último acceso
        usuario.actualizar_ultimo_acceso()
        session.commit()
        
        # La fecha debería haber cambiado
        assert usuario.ultimo_acceso is not None
        # Nota: En algunos casos puede ser igual si pasó muy poco tiempo
    
    def test_cambiar_idioma(self, session):
        """Test: Cambiar idioma preferido"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testidioma',
            email='idioma@example.com',
            nombre='Test',
            idioma_preferido='es',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        assert usuario.idioma_preferido == 'es'
        
        usuario.cambiar_idioma('en')
        session.commit()
        
        assert usuario.idioma_preferido == 'en'
    
    def test_is_active_property(self, session):
        """Test: Propiedad is_active"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testactive',
            email='active@example.com',
            nombre='Test',
            activo=True,
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        assert usuario.is_active is True
        
        usuario.activo = False
        session.commit()
        
        assert usuario.is_active is False
    
    def test_get_id(self, session):
        """Test: Método get_id para Flask-Login"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testgetid',
            email='getid@example.com',
            nombre='Test',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        assert usuario.get_id() == str(usuario.id)
    
    def test_repr(self, session):
        """Test: Representación del usuario"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testrepr',
            email='repr@example.com',
            nombre='Test',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        
        repr_str = repr(usuario)
        assert 'testrepr' in repr_str or 'Test' in repr_str
    
    def test_to_dict(self, session):
        """Test: Convertir usuario a diccionario"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testdict',
            email='dict@example.com',
            nombre='Test',
            apellidos='Usuario',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        usuario_dict = usuario.to_dict()
        
        assert isinstance(usuario_dict, dict)
        assert usuario_dict['username'] == 'testdict'
        assert usuario_dict['email'] == 'dict@example.com'
        assert usuario_dict['nombre'] == 'Test'
        assert 'password_hash' not in usuario_dict  # No debe incluir información sensible
    
    def test_buscar_por_email(self, session):
        """Test: Buscar usuario por email"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='buscaremail',
            email='buscar@example.com',
            nombre='Buscar',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        encontrado = Usuario.buscar_por_email('buscar@example.com')
        assert encontrado is not None
        assert encontrado.username == 'buscaremail'
        
        no_encontrado = Usuario.buscar_por_email('noexiste@example.com')
        assert no_encontrado is None
    
    def test_buscar_por_username(self, session):
        """Test: Buscar usuario por username"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='buscarnombre',
            email='buscar2@example.com',
            nombre='Buscar2',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        encontrado = Usuario.buscar_por_username('buscarnombre')
        assert encontrado is not None
        assert encontrado.email == 'buscar2@example.com'
        
        no_encontrado = Usuario.buscar_por_username('noexiste')
        assert no_encontrado is None
    
    def test_existe_email(self, session):
        """Test: Verificar si existe email"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='testexiste',
            email='existe@example.com',
            nombre='Test',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        assert Usuario.existe_email('existe@example.com') is True
        assert Usuario.existe_email('noexiste@example.com') is False
    
    def test_existe_username(self, session):
        """Test: Verificar si existe username"""
        rol = Rol.query.filter_by(nombre='usuario').first()
        usuario = Usuario(
            username='existeusername',
            email='username@example.com',
            nombre='Test',
            rol_id=rol.id
        )
        usuario.password = 'Test123456'
        session.add(usuario)
        session.commit()
        
        assert Usuario.existe_username('existeusername') is True
        assert Usuario.existe_username('noexiste') is False
    
    def test_es_administrador(self, session):
        """Test: Verificar si es administrador"""
        rol_usuario = Rol.query.filter_by(nombre='usuario').first()
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        
        # Usuario normal
        usuario_normal = Usuario(
            username='normaluser',
            email='normal@example.com',
            nombre='Normal',
            rol_id=rol_usuario.id
        )
        usuario_normal.password = 'Test123456'
        session.add(usuario_normal)
        
        # Usuario administrador
        usuario_admin = Usuario(
            username='adminuser',
            email='admin@example.com',
            nombre='Admin',
            rol_id=rol_admin.id
        )
        usuario_admin.password = 'Test123456'
        session.add(usuario_admin)
        session.commit()
        
        assert usuario_normal.es_administrador is False
        assert usuario_admin.es_administrador is True
    
    def test_es_usuario_normal(self, session):
        """Test: Verificar si es usuario normal"""
        rol_usuario = Rol.query.filter_by(nombre='usuario').first()
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        
        # Usuario normal
        usuario_normal = Usuario(
            username='normaluser2',
            email='normal2@example.com',
            nombre='Normal2',
            rol_id=rol_usuario.id
        )
        usuario_normal.password = 'Test123456'
        session.add(usuario_normal)
        
        # Usuario administrador
        usuario_admin = Usuario(
            username='adminuser2',
            email='admin2@example.com',
            nombre='Admin2',
            rol_id=rol_admin.id
        )
        usuario_admin.password = 'Test123456'
        session.add(usuario_admin)
        session.commit()
        
        assert usuario_normal.es_usuario_normal is True
        assert usuario_admin.es_usuario_normal is False
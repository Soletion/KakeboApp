"""
Punto de entrada para la aplicación Kakebo
Ejecuta el servidor de desarrollo de Flask
"""
import os
import sys
from dotenv import load_dotenv

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
load_dotenv()

def main():
    """Función principal para ejecutar la aplicación"""
    try:
        # Importar la aplicación
        from app import create_app
        
        # Crear instancia de la aplicación
        app = create_app()
        
        # Obtener configuración
        debug = app.config.get('DEBUG', False)
        host = os.environ.get('FLASK_HOST', '127.0.0.1')
        port = int(os.environ.get('FLASK_PORT', 5000))
        
        # Mostrar información de inicio
        print(f"\n{'='*50}")
        print(f" Iniciando Kakebo - {app.config.get('APP_NAME')} v{app.config.get('APP_VERSION')}")
        print(f"{'='*50}")
        print(f" Entorno: {os.environ.get('FLASK_ENV', 'development')}")
        print(f" Debug: {debug}")
        print(f" Servidor: http://{host}:{port}")
        print(f" Base de datos: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"{'='*50}\n")
        
        # Ejecutar servidor
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except ImportError as e:
        print(f" Error importando la aplicación: {e}")
        print("   ¿Has instalado las dependencias? (pip install -r requirements.txt)")
        sys.exit(1)
        
    except Exception as e:
        print(f" Error iniciando la aplicación: {e}")
        sys.exit(1)


def create_tables():
    """Función auxiliar para crear tablas en la base de datos"""
    try:
        from app import create_app, db
        from app.models import Usuario, Categoria, Gasto, Ingreso, ObjetivoAhorro
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Tablas creadas correctamente")
            
            # Inicializar categorías
            from app.models.categoria import Categoria
            Categoria.inicializar_categorias()
            print(" Categorías inicializadas")
            
    except Exception as e:
        print(f" Error creando tablas: {e}")
        sys.exit(1)


def seed_database():
    """Función auxiliar para poblar la base de datos con datos de ejemplo"""
    try:
        from app import create_app, db
        from app.models import Usuario, Categoria, Gasto, Ingreso
        from datetime import datetime, timedelta
        import random
        
        app = create_app()
        with app.app_context():
            
            # Crear usuario de prueba
            usuario = Usuario(
                email='demo@kakebo.com',
                username='demo',
                nombre='Usuario',
                apellidos='Demo',
                idioma_preferido='es'
            )
            usuario.password = 'Demo1234'
            db.session.add(usuario)
            db.session.commit()
            
            # Obtener categorías
            categorias = Categoria.query.all()
            
            # Crear gastos de ejemplo (últimos 3 meses)
            for i in range(30):
                fecha = datetime.now() - timedelta(days=random.randint(0, 90))
                gasto = Gasto(
                    usuario_id=usuario.id,
                    categoria_id=random.choice(categorias).id,
                    cantidad=random.uniform(5, 200),
                    fecha=fecha.date(),
                    descripcion=f'Gasto de ejemplo {i+1}'
                )
                db.session.add(gasto)
            
            # Crear ingresos de ejemplo
            for i in range(5):
                fecha = datetime.now() - timedelta(days=random.randint(0, 90))
                ingreso = Ingreso(
                    usuario_id=usuario.id,
                    cantidad=random.uniform(500, 2000),
                    fecha=fecha.date(),
                    descripcion=f'Ingreso de ejemplo {i+1}',
                    es_fijo=(i < 2)  # 2 ingresos fijos
                )
                db.session.add(ingreso)
            
            db.session.commit()
            print(f" Datos de ejemplo creados para usuario 'demo' (password: Demo1234)")
            
    except Exception as e:
        print(f" Error poblando base de datos: {e}")
        db.session.rollback()
        sys.exit(1)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Kakebo - Aplicación de finanzas personales')
    parser.add_argument('--create-db', action='store_true', help='Crear tablas en la base de datos')
    parser.add_argument('--seed', action='store_true', help='Poblar con datos de ejemplo')
    
    args = parser.parse_args()
    
    if args.create_db:
        create_tables()
    elif args.seed:
        seed_database()
    else:
        main()
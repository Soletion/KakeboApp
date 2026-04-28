# Kakebo - Aplicación de Planificación Financiera Personal

Aplicación web para la gestión de finanzas personales basada en el método japonés Kakebo, desarrollada como proyecto de Desarrollo de Aplicaciones Web (DAW).

## Descripción

Kakebo permite a los usuarios llevar un control detallado de sus ingresos y gastos mensuales, clasificándolos según las categorías tradicionales del método Kakebo: gastos esenciales, gastos prescindibles, ocio e imprevistos. La aplicación facilita el establecimiento de objetivos de ahorro y proporciona visualizaciones gráficas del estado financiero.

## Tecnologías Utilizadas

- Backend: Python 3.8+ con Flask 3.0
- Base de datos: MySQL 5.7+
- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript ES6+
- Templating: Jinja2
- Seguridad: bcrypt, sesiones seguras, protección CSRF
- Internacionalización: Sistema i18n con archivos JSON

## Requisitos del Sistema

- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)
- Entorno virtual (recomendado)

## Instalación

1. Clonar el repositorio:
   git clone https://github.com/soletion/kakebo.git
   cd kakebo

2. Crear y activar entorno virtual:
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate

3. Instalar dependencias:
   pip install -r requirements.txt

4. Configurar variables de entorno:
   cp .env.example .env
   # Editar .env con tus configuraciones

5. Crear la base de datos:
   mysql -u root -p < scripts/init_db.sql

6. Iniciar la aplicación:
   python run.py

7. Acceder a la aplicación:
   http://localhost:5000

## Estructura del Proyecto

kakebo/
├── app/               # Código principal de la aplicación
│   ├── controllers/   # Controladores (lógica de negocio)
│   ├── models/        # Modelos de base de datos
│   ├── services/      # Servicios reutilizables
│   ├── static/        # Archivos estáticos (CSS, JS, imágenes)
│   ├── templates/     # Plantillas HTML
│   ├── translations/  # Archivos de traducción
│   └── utils/         # Utilidades y funciones auxiliares
├── tests/             # Pruebas unitarias y de integración
├── docs/              # Documentación del proyecto
├── scripts/           # Scripts de utilidad
└── logs/              # Archivos de log

## Funcionalidades Principales

- Registro y autenticación de usuarios
- Gestión de ingresos mensuales (fijos y variables)
- Registro de gastos con categorías Kakebo
- Definición de objetivos de ahorro mensuales
- Dashboard con resumen financiero
- Gráficos estadísticos de evolución
- Histórico de meses anteriores
- Soporte multiidioma (español/inglés)
- Diseño responsive para todos los dispositivos

## Seguridad

- Contraseñas hasheadas con bcrypt (coste 12)
- Sesiones seguras con cookies HttpOnly, Secure y SameSite
- Protección contra SQL Injection mediante consultas parametrizadas
- Protección contra XSS mediante escape en templates
- Tokens CSRF en formularios
- Validación de datos en cliente y servidor
- Limitación de intentos de login

## Pruebas

Ejecutar el suite de pruebas:

pytest tests/

Con cobertura:

pytest --cov=app tests/

## Despliegue en Producción

1. Configurar servidor Ubuntu Server LTS
2. Instalar y configurar Nginx como proxy inverso
3. Configurar Gunicorn como servidor WSGI
4. Establecer certificado SSL con Let's Encrypt
5. Configurar variables de entorno de producción
6. Ejecutar migraciones de base de datos
7. Iniciar la aplicación con systemd

Ver documentación completa en docs/instalacion.md

## Mantenimiento

- Backups automáticos: Diarios con retención de 30 días
- Actualizaciones: Seguir versionado semántico
- Monitorización: Logs rotativos y alertas por error

## Contribuir

1. Fork del repositorio
2. Crear rama para nueva funcionalidad
3. Desarrollar con pruebas
4. Enviar pull request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.

## Autor

Desarrollado como proyecto educativo para Desarrollo de Aplicaciones Web (DAW).

## Estado del Proyecto

En desarrollo activo - Versión 1.0.0
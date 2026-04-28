# Script de despliegue para Kakebo en producción
# Automatiza el proceso de despliegue en servidor Ubuntu

# Configuración
APP_NAME="kakebo"
APP_USER="kakebo"
APP_DIR="/var/www/$APP_NAME"
REPO_URL="https://github.com/tuusuario/kakebo.git"
BRANCH="main"
VENV_DIR="$APP_DIR/venv"
BACKUP_DIR="/var/backups/$APP_NAME"
LOG_FILE="/var/log/kakebo/deploy.log"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función de logging
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Función de error
error_exit() {
    log_message "${RED}ERROR: $1${NC}"
    exit 1
}

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    error_exit "Este script debe ejecutarse como root"
fi

log_message "${GREEN}=== Iniciando despliegue de Kakebo ===${NC}"

# Verificar requisitos
log_message "Verificando requisitos..."

# Verificar git
if ! command -v git &> /dev/null; then
    log_message "Instalando git..."
    apt-get update && apt-get install -y git || error_exit "No se pudo instalar git"
fi

# Verificar python3
if ! command -v python3 &> /dev/null; then
    log_message "Instalando python3..."
    apt-get update && apt-get install -y python3 python3-pip python3-venv || error_exit "No se pudo instalar python3"
fi

# Verificar nginx
if ! command -v nginx &> /dev/null; then
    log_message "Instalando nginx..."
    apt-get update && apt-get install -y nginx || error_exit "No se pudo instalar nginx"
fi

# Verificar mysql
if ! command -v mysql &> /dev/null; then
    log_message "Instalando mysql..."
    apt-get update && apt-get install -y mysql-server || error_exit "No se pudo instalar mysql"
fi

# Crear usuario de aplicación si no existe
if ! id -u "$APP_USER" &> /dev/null; then
    log_message "Creando usuario $APP_USER..."
    useradd -m -s /bin/bash "$APP_USER" || error_exit "No se pudo crear usuario"
fi

# Crear directorios necesarios
log_message "Creando estructura de directorios..."
mkdir -p "$APP_DIR" "$BACKUP_DIR" "/var/log/$APP_NAME" || error_exit "No se pudo crear directorios"
chown -R "$APP_USER:$APP_USER" "$APP_DIR" "/var/log/$APP_NAME"

# Backup del código actual si existe
if [ -d "$APP_DIR/.git" ]; then
    log_message "Realizando backup del código actual..."
    BACKUP_FILE="$BACKUP_DIR/pre_deploy_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$BACKUP_FILE" -C "$APP_DIR" . || log_message "${YELLOW}Advertencia: No se pudo crear backup${NC}"
fi

# Clonar/actualizar repositorio
log_message "Actualizando código desde $REPO_URL..."
cd "$APP_DIR" || error_exit "No se puede acceder a $APP_DIR"

if [ -d ".git" ]; then
    # Actualizar repo existente
    sudo -u "$APP_USER" git fetch origin || error_exit "Error fetching repository"
    sudo -u "$APP_USER" git reset --hard "origin/$BRANCH" || error_exit "Error resetting repository"
else
    # Clonar nuevo repo
    sudo -u "$APP_USER" git clone -b "$BRANCH" "$REPO_URL" . || error_exit "Error cloning repository"
fi

# Crear/actualizar entorno virtual
log_message "Configurando entorno virtual..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u "$APP_USER" python3 -m venv "$VENV_DIR" || error_exit "Error creando entorno virtual"
fi

# Instalar dependencias
log_message "Instalando dependencias Python..."
sudo -u "$APP_USER" bash -c "source $VENV_DIR/bin/activate && pip install --upgrade pip" || error_exit "Error actualizando pip"
sudo -u "$APP_USER" bash -c "source $VENV_DIR/bin/activate && pip install -r $APP_DIR/requirements.txt" || error_exit "Error instalando dependencias"

# Configurar archivo .env
log_message "Configurando variables de entorno..."
if [ ! -f "$APP_DIR/.env" ]; then
    if [ -f "$APP_DIR/.env.example" ]; then
        sudo -u "$APP_USER" cp "$APP_DIR/.env.example" "$APP_DIR/.env"
        log_message "${YELLOW}  Archivo .env creado. Debes configurarlo manualmente.${NC}"
    else
        error_exit "No se encuentra .env.example"
    fi
fi

# Inicializar base de datos
log_message "Inicializando base de datos..."
sudo -u "$APP_USER" bash -c "source $VENV_DIR/bin/activate && cd $APP_DIR && python run.py --create-db" || log_message "${YELLOW}Advertencia: Error creando tablas${NC}"

# Configurar permisos
log_message "Configurando permisos..."
chown -R "$APP_USER:$APP_USER" "$APP_DIR" "/var/log/$APP_NAME"
chmod -R 755 "$APP_DIR"
chmod 600 "$APP_DIR/.env"

# Configurar Gunicorn
log_message "Configurando Gunicorn..."
cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=Gunicorn instance to serve $APP_NAME
After=network.target mysql.service

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$APP_DIR/$APP_NAME.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
log_message "Configurando Nginx..."
cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/$APP_NAME.sock;
    }
    
    location /static {
        alias $APP_DIR/app/static;
        expires 30d;
    }
    
    location /media {
        alias $APP_DIR/app/media;
        expires 30d;
    }
}
EOF

# Habilitar sitio
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Verificar configuración de Nginx
nginx -t || error_exit "Error en configuración de Nginx"

# Reiniciar servicios
log_message "Reiniciando servicios..."
systemctl daemon-reload
systemctl restart $APP_NAME
systemctl enable $APP_NAME
systemctl restart nginx
systemctl enable nginx

# Verificar estado de servicios
log_message "Verificando servicios..."
sleep 5

if systemctl is-active --quiet $APP_NAME; then
    log_message "${GREEN} Servicio $APP_NAME activo${NC}"
else
    log_message "${RED} Servicio $APP_NAME inactivo${NC}"
    journalctl -u $APP_NAME -n 20 --no-pager
fi

if systemctl is-active --quiet nginx; then
    log_message "${GREEN} Nginx activo${NC}"
else
    log_message "${RED} Nginx inactivo${NC}"
fi

# Verificar conectividad
curl -s http://localhost > /dev/null
if [ $? -eq 0 ]; then
    log_message "${GREEN} Aplicación respondiendo en localhost${NC}"
else
    log_message "${RED} Aplicación no responde${NC}"
fi

log_message "${GREEN}=== Despliegue completado ===${NC}"
log_message "${YELLOW}Próximos pasos:${NC}"
echo "1. Configurar SSL: certbot --nginx -d tudominio.com"
echo "2. Configurar backup automático: crontab -e"
echo "3. Revisar logs: journalctl -u $APP_NAME -f"
echo "4. Acceder a la aplicación: http://$(hostname -I | awk '{print $1}')"
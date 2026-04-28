# Script de backup para la base de datos MySQL de Kakebo
# Realiza backup diario con rotación y compresión

# Configuración
BACKUP_DIR="/var/backups/kakebo"
DB_NAME="kakebo_db"
DB_USER="kakebo_user"
DB_PASSWORD="$(cat /etc/kakebo/db_password)"  # Leer contraseña de archivo seguro
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
LOG_FILE="/var/log/kakebo/backup.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de logging
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Función de error
error_exit() {
    log_message "${RED}ERROR: $1${NC}"
    exit 1
}

# Crear directorios si no existen
mkdir -p "$BACKUP_DIR" || error_exit "No se puede crear directorio de backup"
mkdir -p "$(dirname "$LOG_FILE")" || error_exit "No se puede crear directorio de logs"

log_message "${GREEN}Iniciando backup de base de datos...${NC}"

# Verificar conexión a MySQL
if ! mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "USE $DB_NAME" 2>/dev/null; then
    error_exit "No se puede conectar a la base de datos"
fi

# Nombre del archivo de backup
BACKUP_FILE="$BACKUP_DIR/kakebo_$DATE.sql"
BACKUP_GZ="$BACKUP_FILE.gz"

log_message "Creando backup: $BACKUP_FILE"

# Realizar backup
if mysqldump \
    --user="$DB_USER" \
    --password="$DB_PASSWORD" \
    --host=localhost \
    --databases "$DB_NAME" \
    --add-drop-database \
    --add-drop-table \
    --create-options \
    --complete-insert \
    --comments \
    --disable-keys \
    --dump-date \
    --extended-insert \
    --quick \
    --routines \
    --triggers \
    --single-transaction \
    > "$BACKUP_FILE" 2>> "$LOG_FILE"; then
    
    log_message "${GREEN}Backup creado exitosamente${NC}"
    
    # Comprimir backup
    log_message "Comprimiendo backup..."
    if gzip "$BACKUP_FILE"; then
        log_message "${GREEN}Backup comprimido: $BACKUP_GZ${NC}"
        
        # Crear enlace simbólico al último backup
        ln -sf "$BACKUP_GZ" "$BACKUP_DIR/latest.sql.gz"
        
        # Verificar integridad del backup
        if gzip -t "$BACKUP_GZ" 2>/dev/null; then
            log_message "${GREEN}Verificación de integridad exitosa${NC}"
        else
            log_message "${RED}ADVERTENCIA: El backup puede estar corrupto${NC}"
        fi
        
        # Obtener tamaño del backup
        SIZE=$(du -h "$BACKUP_GZ" | cut -f1)
        log_message "Tamaño del backup: $SIZE"
        
    else
        error_exit "Error comprimiendo backup"
    fi
else
    error_exit "Error creando backup"
fi

# Rotación de backups (eliminar antiguos)
log_message "Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
find "$BACKUP_DIR" -name "kakebo_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# Contar backups actuales
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "kakebo_*.sql.gz" -type f | wc -l)
log_message "Total de backups disponibles: $BACKUP_COUNT"

# Verificar espacio en disco
DISK_USAGE=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $5}')
DISK_AVAILABLE=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $4}')
log_message "Espacio en disco: $DISK_USAGE usado, $DISK_AVAILABLE disponible"

# Backup adicional a ubicación remota 
if [ -f "/etc/kakebo/remote_backup.conf" ]; then
    log_message "Realizando backup remoto..."
    source /etc/kakebo/remote_backup.conf
    
    if [ -n "$REMOTE_HOST" ] && [ -n "$REMOTE_PATH" ]; then
        scp "$BACKUP_GZ" "$REMOTE_HOST:$REMOTE_PATH/" 2>> "$LOG_FILE" && \
            log_message "${GREEN}Backup remoto completado${NC}" || \
            log_message "${RED}Error en backup remoto${NC}"
    fi
fi

# Enviar notificación 
if command -v sendmail &> /dev/null; then
    MAIL_TO="admin@kakebo.com"
    MAIL_SUBJECT="Backup completado - Kakebo"
    MAIL_BODY="Backup completado: $BACKUP_GZ ($SIZE)"
    echo "$MAIL_BODY" | sendmail "$MAIL_TO"
fi

log_message "${GREEN}Proceso de backup finalizado${NC}"
exit 0
#!/bin/bash
# Script de restauración para la base de datos MySQL de Kakebo
# Uso: ./restore_db.sh [archivo_backup.sql.gz]

# Configuración
BACKUP_DIR="/var/backups/kakebo"
DB_NAME="kakebo_db"
DB_USER="kakebo_user"
DB_PASSWORD="$(cat /etc/kakebo/db_password)"
LOG_FILE="/var/log/kakebo/restore.log"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIONES] [archivo_backup]"
    echo ""
    echo "Opciones:"
    echo "  -l, --latest     Restaurar el último backup disponible"
    echo "  -f, --file FILE  Restaurar un archivo específico"
    echo "  -d, --date DATE  Restaurar backup de una fecha (YYYYMMDD)"
    echo "  -l, --list       Listar backups disponibles"
    echo "  -h, --help       Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --latest"
    echo "  $0 --file backup.sql.gz"
    echo "  $0 --date 20240115"
}

# Listar backups disponibles
list_backups() {
    echo -e "${YELLOW}Backups disponibles:${NC}"
    echo "------------------------"
    ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null | awk '{print $9 " (" $5 ")"}' || echo "No hay backups"
    exit 0
}

# Confirmar restauración
confirm_restore() {
    echo -e "${RED}⚠️  ¡ATENCIÓN! Esta acción SOBREESCRIBIRÁ la base de datos actual.${NC}"
    echo -e "Base de datos: ${YELLOW}$DB_NAME${NC}"
    echo -e "Backup a restaurar: ${YELLOW}$1${NC}"
    read -p "¿Estás seguro? (escribe 'RESTAURAR' para confirmar): " confirmation
    
    if [ "$confirmation" != "RESTAURAR" ]; then
        error_exit "Restauración cancelada por el usuario"
    fi
}

# Verificar que el backup existe
check_backup() {
    if [ ! -f "$1" ]; then
        error_exit "Archivo de backup no encontrado: $1"
    fi
}

# Restaurar backup
restore_backup() {
    local backup_file="$1"
    
    log_message "${GREEN}Iniciando restauración desde: $backup_file${NC}"
    
    # Verificar integridad
    log_message "Verificando integridad del backup..."
    if ! gzip -t "$backup_file" 2>/dev/null; then
        error_exit "El archivo de backup está corrupto"
    fi
    
    # Crear backup automático antes de restaurar
    log_message "Creando backup de seguridad pre-restauración..."
    ./backup_db.sh
    
    # Confirmar restauración
    confirm_restore "$backup_file"
    
    # Descomprimir temporalmente
    TEMP_FILE="/tmp/restore_$$.sql"
    log_message "Descomprimiendo backup..."
    if ! gunzip -c "$backup_file" > "$TEMP_FILE"; then
        rm -f "$TEMP_FILE"
        error_exit "Error descomprimiendo backup"
    fi
    
    # Restaurar base de datos
    log_message "Restaurando base de datos..."
    if mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$TEMP_FILE" 2>> "$LOG_FILE"; then
        log_message "${GREEN}✅ Restauración completada exitosamente${NC}"
        
        # Limpiar archivo temporal
        rm -f "$TEMP_FILE"
        
        # Verificar restauración
        log_message "Verificando restauración..."
        TABLE_COUNT=$(mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DB_NAME'" | tail -1)
        log_message "Tablas restauradas: $TABLE_COUNT"
        
    else
        rm -f "$TEMP_FILE"
        error_exit "Error restaurando base de datos"
    fi
}

# Procesar argumentos
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

while [ $# -gt 0 ]; do
    case "$1" in
        -l|--latest)
            LATEST=$(ls -t "$BACKUP_DIR"/*.sql.gz 2>/dev/null | head -1)
            if [ -z "$LATEST" ]; then
                error_exit "No hay backups disponibles"
            fi
            restore_backup "$LATEST"
            shift
            ;;
        -f|--file)
            if [ -z "$2" ]; then
                error_exit "Debe especificar un archivo"
            fi
            if [[ "$2" = /* ]]; then
                BACKUP_FILE="$2"
            else
                BACKUP_FILE="$BACKUP_DIR/$2"
            fi
            check_backup "$BACKUP_FILE"
            restore_backup "$BACKUP_FILE"
            shift 2
            ;;
        -d|--date)
            if [ -z "$2" ]; then
                error_exit "Debe especificar una fecha (YYYYMMDD)"
            fi
            BACKUP_FILE="$BACKUP_DIR/kakebo_${2}*.sql.gz"
            if ! ls $BACKUP_FILE 2>/dev/null; then
                error_exit "No hay backup para la fecha: $2"
            fi
            restore_backup $(ls $BACKUP_FILE | head -1)
            shift 2
            ;;
        -l|--list)
            list_backups
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            # Asumir que es un archivo
            if [[ "$1" = /* ]]; then
                BACKUP_FILE="$1"
            else
                BACKUP_FILE="$BACKUP_DIR/$1"
            fi
            check_backup "$BACKUP_FILE"
            restore_backup "$BACKUP_FILE"
            shift
            ;;
    esac
done
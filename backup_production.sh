#!/bin/bash

# Production Backup Script for Art Explorer
# This script handles database and file backups for production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="art-explorer"
DOCKER_COMPOSE_FILE="docker/docker-compose.prod.yml"
ENV_FILE=".env.production"
BACKUP_DIR="backups"
RETENTION_DAYS=30

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
        error "Production Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi
    
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Production environment file not found: $ENV_FILE"
        exit 1
    fi
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    success "Prerequisites check passed"
}

# Load environment variables
load_environment() {
    log "Loading environment variables..."
    
    if [[ -f "$ENV_FILE" ]]; then
        source "$ENV_FILE"
        success "Environment variables loaded"
    else
        error "Could not load environment variables"
        exit 1
    fi
}

# Backup database
backup_database() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/database_backup_${timestamp}.sql"
    
    log "Creating database backup..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_dump \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --clean \
        --if-exists \
        --create \
        --verbose \
        > "$backup_file" 2>/dev/null; then
        
        # Compress the backup
        gzip "$backup_file"
        local compressed_file="${backup_file}.gz"
        
        # Get file size
        local file_size=$(du -h "$compressed_file" | cut -f1)
        
        success "Database backup created: $compressed_file ($file_size)"
        echo "$compressed_file" >> "$BACKUP_DIR/database_backups.txt"
        
        return 0
    else
        error "Database backup failed"
        return 1
    fi
}

# Backup uploads directory
backup_uploads() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/uploads_backup_${timestamp}.tar.gz"
    
    log "Creating uploads backup..."
    
    if tar -czf "$backup_file" uploads/ 2>/dev/null; then
        local file_size=$(du -h "$backup_file" | cut -f1)
        success "Uploads backup created: $backup_file ($file_size)"
        echo "$backup_file" >> "$BACKUP_DIR/uploads_backups.txt"
        return 0
    else
        error "Uploads backup failed"
        return 1
    fi
}

# Backup logs
backup_logs() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/logs_backup_${timestamp}.tar.gz"
    
    log "Creating logs backup..."
    
    if tar -czf "$backup_file" logs/ 2>/dev/null; then
        local file_size=$(du -h "$backup_file" | cut -f1)
        success "Logs backup created: $backup_file ($file_size)"
        echo "$backup_file" >> "$BACKUP_DIR/logs_backups.txt"
        return 0
    else
        warning "Logs backup failed (logs directory may not exist)"
        return 1
    fi
}

# Backup environment configuration
backup_config() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/config_backup_${timestamp}.tar.gz"
    
    log "Creating configuration backup..."
    
    # Create temporary config backup
    local temp_config_dir="/tmp/config_backup_${timestamp}"
    mkdir -p "$temp_config_dir"
    
    # Copy important config files
    cp "$ENV_FILE" "$temp_config_dir/"
    cp "$DOCKER_COMPOSE_FILE" "$temp_config_dir/"
    cp docker/nginx.prod.conf "$temp_config_dir/" 2>/dev/null || true
    cp docker/Dockerfile.* "$temp_config_dir/" 2>/dev/null || true
    
    if tar -czf "$backup_file" -C "$temp_config_dir" . 2>/dev/null; then
        local file_size=$(du -h "$backup_file" | cut -f1)
        success "Configuration backup created: $backup_file ($file_size)"
        echo "$backup_file" >> "$BACKUP_DIR/config_backups.txt"
        
        # Clean up temp directory
        rm -rf "$temp_config_dir"
        return 0
    else
        error "Configuration backup failed"
        rm -rf "$temp_config_dir"
        return 1
    fi
}

# Create backup manifest
create_manifest() {
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local manifest_file="$BACKUP_DIR/backup_manifest_$(date +%Y%m%d_%H%M%S).txt"
    
    log "Creating backup manifest..."
    
    {
        echo "Art Explorer Production Backup Manifest"
        echo "Generated: $timestamp"
        echo "====================================="
        echo ""
        
        echo "Database Backups:"
        if [[ -f "$BACKUP_DIR/database_backups.txt" ]]; then
            cat "$BACKUP_DIR/database_backups.txt" | tail -5
        else
            echo "No database backups found"
        fi
        echo ""
        
        echo "Uploads Backups:"
        if [[ -f "$BACKUP_DIR/uploads_backups.txt" ]]; then
            cat "$BACKUP_DIR/uploads_backups.txt" | tail -5
        else
            echo "No uploads backups found"
        fi
        echo ""
        
        echo "Logs Backups:"
        if [[ -f "$BACKUP_DIR/logs_backups.txt" ]]; then
            cat "$BACKUP_DIR/logs_backups.txt" | tail -5
        else
            echo "No logs backups found"
        fi
        echo ""
        
        echo "Configuration Backups:"
        if [[ -f "$BACKUP_DIR/config_backups.txt" ]]; then
            cat "$BACKUP_DIR/config_backups.txt" | tail -5
        else
            echo "No configuration backups found"
        fi
        echo ""
        
        echo "Total Backup Size:"
        du -sh "$BACKUP_DIR" | cut -f1
        
    } > "$manifest_file"
    
    success "Backup manifest created: $manifest_file"
}

# Clean up old backups
cleanup_old_backups() {
    log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    local deleted_count=0
    
    # Find and delete old database backups
    find "$BACKUP_DIR" -name "database_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null | wc -l | read deleted_count
    if [[ $deleted_count -gt 0 ]]; then
        log "Deleted $deleted_count old database backups"
    fi
    
    # Find and delete old uploads backups
    find "$BACKUP_DIR" -name "uploads_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null | wc -l | read deleted_count
    if [[ $deleted_count -gt 0 ]]; then
        log "Deleted $deleted_count old uploads backups"
    fi
    
    # Find and delete old logs backups
    find "$BACKUP_DIR" -name "logs_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null | wc -l | read deleted_count
    if [[ $deleted_count -gt 0 ]]; then
        log "Deleted $deleted_count old logs backups"
    fi
    
    # Find and delete old config backups
    find "$BACKUP_DIR" -name "config_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null | wc -l | read deleted_count
    if [[ $deleted_count -gt 0 ]]; then
        log "Deleted $deleted_count old config backups"
    fi
    
    # Clean up old manifest files
    find "$BACKUP_DIR" -name "backup_manifest_*.txt" -mtime +$RETENTION_DAYS -delete 2>/dev/null | wc -l | read deleted_count
    if [[ $deleted_count -gt 0 ]]; then
        log "Deleted $deleted_count old manifest files"
    fi
    
    success "Cleanup completed"
}

# Verify backup integrity
verify_backups() {
    log "Verifying backup integrity..."
    
    local verification_passed=true
    
    # Verify database backup
    local latest_db_backup=$(find "$BACKUP_DIR" -name "database_backup_*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    if [[ -n "$latest_db_backup" ]]; then
        if gzip -t "$latest_db_backup" 2>/dev/null; then
            success "Database backup verification passed"
        else
            error "Database backup verification failed"
            verification_passed=false
        fi
    fi
    
    # Verify uploads backup
    local latest_uploads_backup=$(find "$BACKUP_DIR" -name "uploads_backup_*.tar.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    if [[ -n "$latest_uploads_backup" ]]; then
        if gzip -t "$latest_uploads_backup" 2>/dev/null; then
            success "Uploads backup verification passed"
        else
            error "Uploads backup verification failed"
            verification_passed=false
        fi
    fi
    
    if [[ "$verification_passed" == "true" ]]; then
        success "All backup verifications passed"
    else
        warning "Some backup verifications failed"
    fi
}

# Show backup status
show_status() {
    log "Backup status:"
    echo ""
    
    echo "Database Backups:"
    ls -lh "$BACKUP_DIR"/database_backup_*.sql.gz 2>/dev/null | tail -3 || echo "No database backups found"
    echo ""
    
    echo "Uploads Backups:"
    ls -lh "$BACKUP_DIR"/uploads_backup_*.tar.gz 2>/dev/null | tail -3 || echo "No uploads backups found"
    echo ""
    
    echo "Logs Backups:"
    ls -lh "$BACKUP_DIR"/logs_backup_*.tar.gz 2>/dev/null | tail -3 || echo "No logs backups found"
    echo ""
    
    echo "Configuration Backups:"
    ls -lh "$BACKUP_DIR"/config_backup_*.tar.gz 2>/dev/null | tail -3 || echo "No configuration backups found"
    echo ""
    
    echo "Total Backup Directory Size:"
    du -sh "$BACKUP_DIR" | cut -f1
}

# Main backup function
main() {
    log "Starting production backup process..."
    
    check_prerequisites
    load_environment
    
    # Create backups
    backup_database
    backup_uploads
    backup_logs
    backup_config
    
    # Create manifest and cleanup
    create_manifest
    cleanup_old_backups
    verify_backups
    
    # Show status
    show_status
    
    success "Production backup completed successfully!"
    
    echo ""
    log "Backup files are stored in: $BACKUP_DIR"
    log "Consider setting up automated backups with cron:"
    echo "0 2 * * * cd $(pwd) && ./backup_production.sh >> backup.log 2>&1"
}

# Run main function
main "$@"

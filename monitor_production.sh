#!/bin/bash

# Production Monitoring Script for Art Explorer
# This script monitors the health of all production services

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

# Check if services are running
check_services() {
    log "Checking Docker services status..."
    
    if [[ -f "$DOCKER_COMPOSE_FILE" ]]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    else
        error "Production Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        return 1
    fi
}

# Check backend health
check_backend_health() {
    log "Checking backend health..."
    
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        success "Backend is healthy"
        return 0
    else
        error "Backend health check failed"
        return 1
    fi
}

# Check frontend health
check_frontend_health() {
    log "Checking frontend health..."
    
    if curl -f http://localhost:3000/ > /dev/null 2>&1; then
        success "Frontend is healthy"
        return 0
    else
        error "Frontend health check failed"
        return 1
    fi
}

# Check database connection
check_database() {
    log "Checking database connection..."
    
    if [[ -f "$ENV_FILE" ]]; then
        source "$ENV_FILE"
        
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
            success "Database connection is healthy"
            return 0
        else
            error "Database connection check failed"
            return 1
        fi
    else
        warning "Environment file not found, skipping database check"
        return 1
    fi
}

# Check Redis connection
check_redis() {
    log "Checking Redis connection..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
        success "Redis is healthy"
        return 0
    else
        error "Redis health check failed"
        return 1
    fi
}

# Check SSL certificates
check_ssl() {
    log "Checking SSL certificates..."
    
    if [[ -f "docker/ssl/myassemblage.art.crt" ]] && [[ -f "docker/ssl/myassemblage.art.key" ]]; then
        success "SSL certificates found"
        
        # Check certificate expiration
        if command -v openssl &> /dev/null; then
            EXPIRY=$(openssl x509 -enddate -noout -in docker/ssl/myassemblage.art.crt | cut -d= -f2)
            EXPIRY_DATE=$(date -d "$EXPIRY" +%s)
            CURRENT_DATE=$(date +%s)
            DAYS_LEFT=$(( (EXPIRY_DATE - CURRENT_DATE) / 86400 ))
            
            if [[ $DAYS_LEFT -gt 30 ]]; then
                success "SSL certificate expires in $DAYS_LEFT days"
            elif [[ $DAYS_LEFT -gt 7 ]]; then
                warning "SSL certificate expires in $DAYS_LEFT days"
            else
                error "SSL certificate expires in $DAYS_LEFT days - RENEW IMMEDIATELY!"
            fi
        fi
    else
        error "SSL certificates not found"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    log "Checking disk space..."
    
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [[ $DISK_USAGE -lt 80 ]]; then
        success "Disk usage: ${DISK_USAGE}%"
    elif [[ $DISK_USAGE -lt 90 ]]; then
        warning "Disk usage: ${DISK_USAGE}% - Consider cleanup"
    else
        error "Disk usage: ${DISK_USAGE}% - CRITICAL!"
    fi
}

# Check memory usage
check_memory() {
    log "Checking memory usage..."
    
    if command -v free &> /dev/null; then
        MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
        
        if [[ $MEMORY_USAGE -lt 80 ]]; then
            success "Memory usage: ${MEMORY_USAGE}%"
        elif [[ $MEMORY_USAGE -lt 90 ]]; then
            warning "Memory usage: ${MEMORY_USAGE}% - Monitor closely"
        else
            error "Memory usage: ${MEMORY_USAGE}% - HIGH USAGE!"
        fi
    else
        warning "Could not check memory usage (free command not available)"
    fi
}

# Check container resource usage
check_container_resources() {
    log "Checking container resource usage..."
    
    if command -v docker &> /dev/null; then
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
    else
        warning "Docker not available for resource monitoring"
    fi
}

# Check logs for errors
check_logs() {
    log "Checking recent logs for errors..."
    
    if [[ -f "$DOCKER_COMPOSE_FILE" ]]; then
        # Check backend logs for errors
        BACKEND_ERRORS=$(docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=100 backend 2>/dev/null | grep -i "error\|exception\|traceback" | wc -l)
        
        if [[ $BACKEND_ERRORS -eq 0 ]]; then
            success "No recent backend errors found"
        else
            warning "Found $BACKEND_ERRORS recent backend errors"
        fi
        
        # Check nginx logs for errors
        NGINX_ERRORS=$(docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=100 nginx 2>/dev/null | grep -i "error" | wc -l)
        
        if [[ $NGINX_ERRORS -eq 0 ]]; then
            success "No recent nginx errors found"
        else
            warning "Found $NGINX_ERRORS recent nginx errors"
        fi
    else
        warning "Could not check logs (Docker Compose file not found)"
    fi
}

# Generate health report
generate_report() {
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local report_file="health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    log "Generating health report: $report_file"
    
    {
        echo "Art Explorer Production Health Report"
        echo "Generated: $timestamp"
        echo "=================================="
        echo ""
        
        echo "Service Status:"
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps 2>/dev/null || echo "Could not get service status"
        echo ""
        
        echo "Resource Usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || echo "Could not get resource usage"
        echo ""
        
        echo "Recent Errors:"
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=50 2>/dev/null | grep -i "error\|exception\|traceback" || echo "No recent errors found"
        
    } > "$report_file"
    
    success "Health report generated: $report_file"
}

# Main monitoring function
main() {
    log "Starting production health monitoring..."
    
    local overall_health=0
    
    # Run all health checks
    check_services || overall_health=1
    echo ""
    
    check_backend_health || overall_health=1
    check_frontend_health || overall_health=1
    check_database || overall_health=1
    check_redis || overall_health=1
    check_ssl || overall_health=1
    echo ""
    
    check_disk_space
    check_memory
    echo ""
    
    check_container_resources
    echo ""
    
    check_logs
    echo ""
    
    # Generate report
    generate_report
    
    # Summary
    echo ""
    if [[ $overall_health -eq 0 ]]; then
        success "All critical services are healthy!"
    else
        error "Some services have issues. Please review the output above."
    fi
    
    echo ""
    log "Health monitoring completed. Check $report_file for detailed report."
}

# Run main function
main "$@"

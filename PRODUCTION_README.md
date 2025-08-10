# Art Explorer - Production Deployment Guide

This guide covers the complete production deployment process for the Art Explorer application.

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd "Art App"
   cp PRODUCTION_ENV_TEMPLATE.txt .env.production
   # Edit .env.production with your actual values
   ```

2. **Deploy:**
   ```bash
   chmod +x deploy_production.sh
   ./deploy_production.sh
   ```

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 20GB+ disk space
- Domain name with SSL certificate

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Application
ENVIRONMENT=production
SECRET_KEY=your_32_character_secret_key_here
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# API Keys
SMITHSONIAN_API_KEY=your_key_here
MET_API_KEY=your_key_here
```

### Generate Secret Key

```bash
# Option 1: Using OpenSSL
openssl rand -hex 32

# Option 2: Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🐳 Docker Deployment

### Production Docker Compose

```bash
# Start all services
docker-compose -f docker/docker-compose.prod.yml up -d

# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.prod.yml down
```

### Service Architecture

- **Frontend**: Vue.js SPA served by Nginx
- **Backend**: FastAPI with Gunicorn workers
- **Database**: PostgreSQL with optimized settings
- **Cache**: Redis for session and image caching
- **Proxy**: Nginx with SSL termination and rate limiting
- **Monitoring**: Prometheus + Grafana (optional)

## 🔒 Security Features

### Implemented Security Measures

- **Rate Limiting**: API endpoints protected against abuse
- **CORS**: Strict origin validation
- **Security Headers**: HSTS, CSP, XSS protection
- **Input Validation**: Request validation and sanitization
- **Authentication**: JWT-based with secure token handling
- **File Upload**: Size limits and type validation
- **HTTPS**: SSL/TLS enforcement
- **Trusted Hosts**: Host header validation

### Security Checklist

- [ ] Strong SECRET_KEY generated
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Database credentials secured
- [ ] API keys stored in environment variables
- [ ] File permissions set correctly (600 for .env files)
- [ ] Firewall rules configured
- [ ] Regular security updates scheduled

## 📊 Monitoring & Health Checks

### Health Endpoints

- **Backend Health**: `GET /health`
- **Startup Health**: `GET /startup-health`
- **Database Status**: Checked automatically on startup

### Metrics Endpoints

- **Prometheus Metrics**: `GET /metrics`
- **Application Metrics**: Request timing, error rates
- **Database Metrics**: Connection pool status

### Logging

- **Log Level**: Configurable (INFO for production)
- **Log Files**: Rotated automatically
- **Structured Logging**: JSON format for production

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database status
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_isready

# Check logs
docker-compose -f docker/docker-compose.prod.yml logs postgres
```

#### Backend Not Starting
```bash
# Check backend logs
docker-compose -f docker/docker-compose.prod.yml logs backend

# Check environment variables
docker-compose -f docker/docker-compose.prod.yml exec backend env | grep -E "(DATABASE|REDIS|SECRET)"
```

#### Frontend Not Loading
```bash
# Check frontend logs
docker-compose -f docker/docker-compose.prod.yml logs frontend

# Check nginx configuration
docker-compose -f docker/docker-compose.prod.yml exec nginx nginx -t
```

### Performance Issues

#### High Memory Usage
```bash
# Check container resource usage
docker stats

# Restart services with resource limits
docker-compose -f docker/docker-compose.prod.yml restart
```

#### Slow Database Queries
```bash
# Check database performance
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 🔄 Maintenance

### Regular Tasks

#### Daily
- Check application logs for errors
- Monitor resource usage
- Verify backup completion

#### Weekly
- Review security logs
- Check for dependency updates
- Validate SSL certificate expiration

#### Monthly
- Database maintenance (VACUUM, ANALYZE)
- Log rotation and cleanup
- Security audit review

### Backup Procedures

#### Database Backup
```bash
# Manual backup
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup (add to crontab)
0 2 * * * cd /path/to/app && docker-compose -f docker/docker-compose.prod.yml exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > /backups/backup_$(date +\%Y\%m\%d).sql
```

#### File Backup
```bash
# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz logs/
```

## 📈 Scaling

### Vertical Scaling
- Increase container memory/CPU limits
- Optimize database connection pools
- Add more Gunicorn workers

### Horizontal Scaling
- Load balancer with multiple backend instances
- Database read replicas
- Redis cluster for caching

## 🆘 Emergency Procedures

### Service Recovery
```bash
# Restart all services
docker-compose -f docker/docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker/docker-compose.prod.yml restart backend

# Rollback to previous version
git checkout <previous-tag>
./deploy_production.sh
```

### Data Recovery
```bash
# Restore database from backup
docker-compose -f docker/docker-compose.prod.yml exec -T postgres psql -U $POSTGRES_USER -d $POSTGRES_DB < backup_file.sql

# Restore files
tar -xzf uploads_backup_file.tar.gz
```

## 📞 Support

### Contact Information
- **Technical Issues**: [Your Contact]
- **Security Issues**: [Security Contact]
- **Documentation**: [Documentation URL]

### Useful Commands
```bash
# View all running containers
docker ps

# View service logs
docker-compose -f docker/docker-compose.prod.yml logs -f [service_name]

# Access container shell
docker-compose -f docker/docker-compose.prod.yml exec [service_name] sh

# Check service health
curl http://localhost:8001/health
curl http://localhost:3000/
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Production Guide](https://vuejs.org/guide/best-practices/production-deployment.html)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/runtime-config-query.html)
- [Nginx Security Best Practices](https://nginx.org/en/docs/http/ngx_http_core_module.html)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

---

**⚠️ Important**: This is a production deployment. Always test changes in a staging environment first and maintain regular backups of your data and configuration.

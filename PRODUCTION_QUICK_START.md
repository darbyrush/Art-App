# 🚀 Art Explorer Production Quick Start

Get your Art Explorer app running in production in under 10 minutes!

## ⚡ Quick Setup (5 minutes)

### 1. Run the Setup Script
```bash
./setup_production.sh
```

This script will:
- ✅ Create `.env.production` from template
- ✅ Generate a secure SECRET_KEY
- ✅ Set proper file permissions
- ✅ Check Docker installation
- ✅ Create necessary directories

### 2. Edit Environment Variables
```bash
nano .env.production
```

**Required changes:**
- `POSTGRES_PASSWORD` - Set a strong database password
- `REDIS_PASSWORD` - Set a strong Redis password
- `DATABASE_URL` - Update with your database details
- `CORS_ORIGINS` - Set your actual domain
- `ALLOWED_HOSTS` - Set your actual domain

### 3. Deploy to Production
```bash
./deploy_production.sh
```

## 🔧 Manual Setup (Alternative)

### 1. Create Production Environment
```bash
cp PRODUCTION_ENV_TEMPLATE.txt .env.production
```

### 2. Generate Secret Key
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output to `SECRET_KEY` in `.env.production`

### 3. Set File Permissions
```bash
chmod 600 .env.production
```

### 4. Create Directories
```bash
mkdir -p docker/ssl uploads/profile_pictures logs backups
```

## 🌐 Domain & SSL Setup

### 1. Domain Configuration
Update these in `.env.production`:
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
VITE_API_BASE_URL=https://yourdomain.com/api
```

### 2. SSL Certificates
Place your SSL certificates in `docker/ssl/`:
- `myassemblage.art.crt` - Your SSL certificate
- `myassemblage.art.key` - Your private key

**Get free SSL certificates:**
```bash
# Using Let's Encrypt (recommended)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

## 🗄️ Database Setup

### Option 1: Local PostgreSQL (Docker)
The production setup includes a local PostgreSQL container. Just set:
```bash
POSTGRES_PASSWORD=your_secure_password
```

### Option 2: External Database
Update `DATABASE_URL` in `.env.production`:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

## 🔑 API Keys Setup

Get API keys from these services and add to `.env.production`:
- **Smithsonian**: https://api.si.edu/
- **Met Museum**: https://metmuseum.github.io/
- **Harvard**: https://github.com/harvardartmuseums/api-docs
- **Cleveland**: https://openaccess-api.clevelandart.org/
- **Europeana**: https://pro.europeana.eu/page/get-api

## 🚀 Deploy Commands

### Start Production Services
```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Check Service Status
```bash
docker-compose -f docker/docker-compose.prod.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker/docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker/docker-compose.prod.yml logs -f backend
```

### Stop Services
```bash
docker-compose -f docker/docker-compose.prod.yml down
```

## 📊 Monitoring & Health

### Health Check
```bash
./monitor_production.sh
```

### Manual Health Checks
```bash
# Backend health
curl http://localhost:8001/health

# Frontend health
curl http://localhost:3000/

# Database health
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_isready
```

## 💾 Backup & Recovery

### Create Backup
```bash
./backup_production.sh
```

### Automated Backups (Cron)
```bash
# Add to crontab
0 2 * * * cd /path/to/art-app && ./backup_production.sh >> backup.log 2>&1
```

## 🔒 Security Checklist

- [ ] Strong passwords set for all services
- [ ] SSL certificates configured
- [ ] Environment file permissions set to 600
- [ ] Firewall rules configured
- [ ] Regular security updates scheduled
- [ ] Monitoring and alerting configured

## 🚨 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check logs
docker-compose -f docker/docker-compose.prod.yml logs

# Check environment variables
docker-compose -f docker/docker-compose.prod.yml config
```

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_isready

# Check database logs
docker-compose -f docker/docker-compose.prod.yml logs postgres
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in docker/ssl/myassemblage.art.crt -text -noout

# Check nginx configuration
docker-compose -f docker/docker-compose.prod.yml exec nginx nginx -t
```

### Performance Issues

#### High Memory Usage
```bash
# Check container resources
docker stats

# Restart services
docker-compose -f docker/docker-compose.prod.yml restart
```

#### Slow Database
```bash
# Check database performance
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 📈 Scaling

### Vertical Scaling
Increase container resources in `docker/docker-compose.prod.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
```

### Horizontal Scaling
- Load balancer with multiple backend instances
- Database read replicas
- Redis cluster for caching

## 🔄 Maintenance

### Regular Tasks
- **Daily**: Check logs for errors
- **Weekly**: Review security logs
- **Monthly**: Database maintenance (VACUUM, ANALYZE)

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./deploy_production.sh
```

## 📞 Support

### Useful Commands
```bash
# View all running containers
docker ps

# Access container shell
docker-compose -f docker/docker-compose.prod.yml exec backend sh

# Check service health
./monitor_production.sh
```

### Documentation
- [Production README](PRODUCTION_README.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](DEPLOYMENT.md)

---

## 🎯 Next Steps

1. **Run setup**: `./setup_production.sh`
2. **Configure environment**: Edit `.env.production`
3. **Deploy**: `./deploy_production.sh`
4. **Monitor**: `./monitor_production.sh`
5. **Backup**: `./backup_production.sh`

Your Art Explorer app will be production-ready with:
- ✅ Secure authentication
- ✅ Rate limiting
- ✅ SSL/TLS encryption
- ✅ Database backups
- ✅ Health monitoring
- ✅ Performance optimization
- ✅ Security headers

**Happy deploying! 🚀**

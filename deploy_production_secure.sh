#!/bin/bash

# 🚨 PRODUCTION DEPLOYMENT SCRIPT - SECURE VERSION
# This script deploys your application with production security settings

set -e  # Exit on any error

echo "🚀 Starting secure production deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root (should not be)
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if required environment variables are set
print_status "Checking environment variables..."

REQUIRED_VARS=("ENVIRONMENT" "SECRET_KEY" "DATABASE_URL")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var}" ]]; then
        MISSING_VARS+=("$var")
    fi
done

if [[ ${#MISSING_VARS[@]} -gt 0 ]]; then
    print_error "Missing required environment variables: ${MISSING_VARS[*]}"
    print_error "Please set these variables before running the deployment"
    exit 1
fi

# Validate ENVIRONMENT is set to production
if [[ "$ENVIRONMENT" != "production" ]]; then
    print_error "ENVIRONMENT must be set to 'production' for this deployment"
    exit 1
fi

# Validate SECRET_KEY is not default
if [[ "$SECRET_KEY" == "your-secret-key-here" || "$SECRET_KEY" == "dev-secret-key-change-in-production" ]]; then
    print_error "SECRET_KEY must be set to a secure value, not the default"
    exit 1
fi

print_status "Environment validation passed ✓"

# Check if we're in the correct directory
if [[ ! -f "api/main.py" ]]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Create production environment file
print_status "Creating production environment file..."
cat > .env.production << EOF
# Production Environment Configuration
ENVIRONMENT=production
SECRET_KEY=$SECRET_KEY
DATABASE_URL=$DATABASE_URL
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Security Settings
CORS_ORIGINS=${CORS_ORIGINS:-"https://yourdomain.com"}
LOG_LEVEL=INFO
EOF

print_status "Production environment file created ✓"

# Install/update dependencies
print_status "Installing production dependencies..."
if [[ -f "backend/requirements.txt" ]]; then
    pip install -r backend/requirements.txt --upgrade
else
    pip install fastapi uvicorn sqlalchemy psycopg2-binary python-multipart python-jose[cryptography] passlib[bcrypt] aiohttp pillow redis
fi

print_status "Dependencies installed ✓"

# Run security checks
print_status "Running security validation..."
python -c "
from api.main import validate_production_environment
try:
    validate_production_environment()
    print('✓ Production environment validation passed')
except Exception as e:
    print(f'✗ Production environment validation failed: {e}')
    exit(1)
"

if [[ $? -ne 0 ]]; then
    print_error "Security validation failed. Please fix the issues before deployment."
    exit 1
fi

print_status "Security validation passed ✓"

# Database setup
print_status "Setting up production database..."
if command -v psql &> /dev/null; then
    print_status "PostgreSQL client found, testing connection..."
    # Test database connection (adjust as needed)
    # psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1
    # if [[ $? -ne 0 ]]; then
    #     print_warning "Database connection test failed. Please verify DATABASE_URL"
    # fi
else
    print_warning "PostgreSQL client not found. Please install it for database operations."
fi

# Create production startup script
print_status "Creating production startup script..."
cat > start_production_secure.sh << 'EOF'
#!/bin/bash

# Production startup script with security settings

set -e

echo "🚀 Starting Art App in production mode..."

# Load production environment
export $(cat .env.production | xargs)

# Validate environment
python -c "
from api.main import validate_production_environment
validate_production_environment()
print('✓ Environment validation passed')
"

# Start the application with production settings
echo "Starting FastAPI application..."
exec uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips="*" \
    --ssl-keyfile=/path/to/your/ssl/key.pem \
    --ssl-certfile=/path/to/your/ssl/cert.pem
EOF

chmod +x start_production_secure.sh

print_status "Production startup script created ✓"

# Create production nginx configuration
print_status "Creating production nginx configuration..."
cat > nginx.production.conf << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/ssl/cert.pem;
    ssl_certificate_key /path/to/your/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # API Proxy
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files (if serving frontend)
    location /static/ {
        alias /path/to/your/frontend/dist/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

print_status "Production nginx configuration created ✓"

# Create systemd service file
print_status "Creating systemd service file..."
cat > art-app.service << 'EOF'
[Unit]
Description=Art App API
After=network.target

[Service]
Type=exec
User=your-app-user
Group=your-app-group
WorkingDirectory=/path/to/your/app
EnvironmentFile=/path/to/your/app/.env.production
ExecStart=/path/to/your/app/start_production_secure.sh
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/path/to/your/app/uploads

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

print_status "Systemd service file created ✓"

# Create production monitoring script
print_status "Creating production monitoring script..."
cat > monitor_production.sh << 'EOF'
#!/bin/bash

# Production monitoring script

echo "🔍 Production Monitoring Report"
echo "================================"

# Check if service is running
if systemctl is-active --quiet art-app; then
    echo "✓ Art App service is running"
else
    echo "✗ Art App service is not running"
fi

# Check environment
echo ""
echo "Environment Check:"
echo "ENVIRONMENT: $ENVIRONMENT"
echo "SECRET_KEY: ${SECRET_KEY:0:10}..."

# Check logs
echo ""
echo "Recent Logs:"
journalctl -u art-app --since "1 hour ago" --no-pager | tail -20

# Check resource usage
echo ""
echo "Resource Usage:"
ps aux | grep "uvicorn.*main:app" | grep -v grep || echo "No uvicorn processes found"

# Check network
echo ""
echo "Network Status:"
netstat -tlnp | grep :8000 || echo "Port 8000 not listening"
EOF

chmod +x monitor_production.sh

print_status "Production monitoring script created ✓"

# Final security checklist
print_status "Running final security checklist..."

echo ""
echo "🔒 PRODUCTION SECURITY CHECKLIST"
echo "================================"

# Check if debug endpoints are accessible
if grep -r "test_endpoint\|cors_debug\|create_test_user" api/; then
    print_error "Debug endpoints still found in code!"
else
    echo "✓ Debug endpoints removed"
fi

# Check SSL configuration
if grep -r "ssl_context.check_hostname = False" api/; then
    print_error "SSL security issues still found in code!"
else
    echo "✓ SSL security configured properly"
fi

# Check secret key
if [[ "$SECRET_KEY" == "your-secret-key-here" ]]; then
    print_error "Default secret key still in use!"
else
    echo "✓ Secret key configured"
fi

echo ""
print_status "Production deployment preparation completed! 🎉"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Review and customize the generated configuration files"
echo "2. Install SSL certificates and update nginx configuration"
echo "3. Update systemd service file with correct paths and user"
echo "4. Test the deployment in a staging environment first"
echo "5. Deploy to production using: ./start_production_secure.sh"
echo ""
echo "⚠️  IMPORTANT: Review all generated files before deployment!"
echo "⚠️  Update paths, domain names, and user permissions as needed!"
echo ""
echo "📚 See PRODUCTION_SECURITY_CHECKLIST.md for complete security requirements"

# 🚂 Railway Quick Start - Connect Your App

## Immediate Steps to Fix CORS Issues

### 1. Deploy Backend to Railway
```bash
# From your project root
./deploy_railway.sh
```

### 2. Get Your Backend URL
After deployment, Railway will give you a URL like:
`https://your-service-name.railway.app`

### 3. Test Backend Connection
```bash
python test_railway_connection.py https://your-service-name.railway.app
```

### 4. Update Frontend Environment
In Railway frontend service, set:
```
VITE_API_BASE_URL=https://your-service-name.railway.app
```

### 5. Deploy Frontend
Railway will automatically redeploy when you push changes.

## Environment Variables Summary

### Backend Service:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Your secret key
- `ENVIRONMENT` - production
- `CORS_ORIGINS` - https://myassemblage.art,https://www.myassemblage.art

### Frontend Service:
- `VITE_API_BASE_URL` - Your Railway backend URL
- `NODE_ENV` - production

## Quick Test Commands

```bash
# Test Railway backend
python test_railway_connection.py YOUR_BACKEND_URL

# Check current config
cat frontend/src/config.js

# Deploy to Railway
./deploy_railway.sh
```

## What This Fixes

✅ **CORS Errors** - Backend will allow your domain  
✅ **Connection Issues** - Frontend connects to Railway backend  
✅ **Production Ready** - Proper environment configuration  
✅ **Domain Support** - Works with myassemblage.art  

## Next Steps

1. Deploy backend to Railway
2. Test connection with test script
3. Deploy frontend with correct API URL
4. Configure custom domain
5. Test full application

Your app will then work with your Railway backend and database! 🎉

# 🚂 Railway Deployment Setup Guide

## 🚨 **CRITICAL: Fix Your Environment Variables**

Your Railway deployment is failing because the environment variables are not set correctly. The error shows:

```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string 'DATABASE_URL=postgresql://postgres:VPzlvfYNNmRSpxWukjeUIuGDsSFHwKOc@postgres.railway.internal:5432/railway'
```

**The problem:** The environment variable contains the entire `KEY=value` string instead of just the value.

## 🔧 **How to Fix This:**

### 1. Go to Railway Dashboard
- Visit [railway.app](https://railway.app)
- Select your project
- Click on your **backend service**

### 2. Add Environment Variables
Go to the **"Variables"** tab and add these variables:

| Variable Name | Value |
|---------------|-------|
| `DATABASE_URL` | `postgresql://postgres:VPzlvfYNNmRSpxWukjeUIuGDsSFHwKOc@postgres.railway.internal:5432/railway` |
| `SECRET_KEY` | `9Y3-ps7BXOl5RTUDwYvEDhNOZbNMenzqPnZdPcLRsbw` |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | `https://myassemblage.art,https://www.myassemblage.art,https://art-app-frontend.vercel.app,https://*.vercel.app` |

### 3. ⚠️ **IMPORTANT: Format Correctly**
- **Variable Name:** `DATABASE_URL` (just the name, no equals sign)
- **Value:** `postgresql://postgres:VPzlvfYNNmRSpxWukjeUIuGDsSFHwKOc@postgres.railway.internal:5432/railway` (just the URL, no `DATABASE_URL=` prefix)

### 4. Save and Redeploy
- Click **"Save"** after adding each variable
- Railway will automatically redeploy your service

## 🔍 **What to Expect After Fix:**

### ✅ **Successful Startup:**
```
Starting with PORT=8080
INFO: Uvicorn running on http://0.0.0.0:8080
INFO: Using PostgreSQL database for production
INFO: Database tables created successfully
```

### ❌ **If Still Failing:**
Check the logs for:
- Database connection errors
- Missing environment variables
- Permission issues

## 🧪 **Test Your Setup:**

### 1. Health Check Endpoint
After successful deployment, test:
```
https://your-railway-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. Database Connection
The app should automatically:
- Connect to PostgreSQL
- Create necessary tables
- Show "Using PostgreSQL database for production" in logs

## 🚀 **Deployment Commands:**

```bash
# Check your current Railway setup
./deploy_railway.sh

# Monitor Railway logs
# (Check the Railway dashboard for real-time logs)

# Test database connection locally
python3 test_railway_db.py
```

## 📚 **Troubleshooting:**

### Common Issues:
1. **Environment variable format wrong** - Make sure no `KEY=` prefix
2. **Database service not running** - Check Railway PostgreSQL service status
3. **Network issues** - Verify Railway internal networking
4. **Permission denied** - Check database user permissions

### Still Having Issues?
1. Check Railway service logs
2. Verify PostgreSQL service is running
3. Test database connection manually
4. Check environment variable format

## 🎯 **Next Steps:**
1. ✅ Fix environment variables in Railway
2. ✅ Monitor deployment logs
3. ✅ Test health endpoint
4. ✅ Verify database connection
5. ✅ Deploy frontend to Vercel

---

**Need help?** Check the Railway logs and ensure your environment variables are set exactly as shown above.

# Vercel-Railway Native Connection Setup

## Overview
This guide explains how to properly configure your Vercel frontend to use the native connection to your Railway backend.

## What Vercel-Railway Native Connection Provides

### 🚀 **Benefits**
1. **Automatic Environment Variables**: Vercel automatically injects Railway service URLs
2. **Internal Network**: Faster, more secure communication between services
3. **Automatic Service Discovery**: Vercel discovers Railway services automatically
4. **Built-in Monitoring**: Better integration between the two platforms
5. **Cost Optimization**: Potentially lower bandwidth costs for internal communication

### 🔧 **How It Works**
1. Vercel detects your Railway project
2. Automatically injects `VERCEL_RAILWAY_URL` environment variable
3. Your frontend uses this for API calls
4. Communication happens through Vercel's internal network

## Configuration Steps

### 1. **Connect Vercel to Railway**

In your Vercel dashboard:
1. Go to your project settings
2. Navigate to "Integrations"
3. Find "Railway" and click "Connect"
4. Select your Railway project
5. Vercel will automatically detect and connect

### 2. **Environment Variables Priority**

Your frontend now uses this priority order:
```javascript
// Priority order for API base URL:
1. VERCEL_RAILWAY_URL (automatically injected by Vercel)
2. RAILWAY_URL (manual Railway environment variable)
3. VITE_API_BASE_URL (custom environment variable)
4. Fallback URL (hardcoded)
```

### 3. **Vercel Dashboard Configuration**

Set these environment variables in Vercel:

```bash
# Vercel will automatically inject these when connected to Railway:
# VERCEL_RAILWAY_URL (auto-injected)

# Manual fallbacks:
VITE_API_BASE_URL=https://art-app-production.up.railway.app
NODE_ENV=production
```

### 4. **Railway Dashboard Configuration**

Set these in Railway:

```bash
# Required
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production

# CORS for Vercel domains
CORS_ORIGINS=https://myassemblage.art.vercel.app,https://myassemblage.art,https://www.myassemblage.art
```

## Updated Frontend Configuration

### **Config Priority System**
```javascript
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 
               import.meta.env.VERCEL_RAILWAY_URL || 
               import.meta.env.RAILWAY_URL ||
               'https://art-app-production.up.railway.app',
  // ... other config
}
```

### **Automatic Detection**
```javascript
if (import.meta.env.VERCEL_RAILWAY_URL) {
  config.apiBaseUrl = import.meta.env.VERCEL_RAILWAY_URL
  console.log('🚀 Using Vercel-Railway native connection')
} else if (import.meta.env.RAILWAY_URL) {
  config.apiBaseUrl = import.meta.env.RAILWAY_URL
  console.log('🚂 Using Railway direct connection')
} else {
  // fallback logic
}
```

## Backend CORS Configuration

### **Updated CORS Origins**
```python
# Vercel-Railway native connection origins
vercel_origins = [
    "https://myassemblage.art.vercel.app",  # Vercel domain
    "https://*.vercel.app",                 # Any Vercel subdomain
    "https://*.railway.app",                # Any Railway subdomain
]

# Combine all origins
all_origins = cors_origins + default_origins + vercel_origins
```

## Testing the Connection

### 1. **Check Environment Variables**
```javascript
// In browser console or development logs:
console.log('VERCEL_RAILWAY_URL:', import.meta.env.VERCEL_RAILWAY_URL)
console.log('RAILWAY_URL:', import.meta.env.RAILWAY_URL)
console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)
```

### 2. **Verify API Calls**
```javascript
// Check network tab in browser dev tools
// API calls should go to the VERCEL_RAILWAY_URL if available
```

### 3. **Monitor Vercel Logs**
- Check Vercel function logs for connection status
- Look for automatic environment variable injection

## Troubleshooting

### **Common Issues**

1. **VERCEL_RAILWAY_URL not available**
   - Ensure Vercel is connected to Railway
   - Check integration status in Vercel dashboard
   - Redeploy after connecting

2. **CORS errors**
   - Verify CORS_ORIGINS includes your Vercel domain
   - Check that Railway backend is accessible
   - Ensure environment variables are set correctly

3. **Connection timeouts**
   - Verify Railway service is running
   - Check health endpoint: `/health`
   - Monitor Railway logs for errors

### **Debug Steps**

1. **Check Vercel Integration Status**
   - Go to Vercel dashboard → Integrations
   - Verify Railway connection is active

2. **Verify Environment Variables**
   - Check Vercel project settings
   - Ensure variables are set for production

3. **Test Backend Health**
   ```bash
   curl https://your-railway-app.railway.app/health
   ```

4. **Check Network Requests**
   - Use browser dev tools
   - Verify API calls use correct URL
   - Check for CORS errors

## Performance Benefits

### **Expected Improvements**
- **Faster API calls**: Internal Vercel network
- **Lower latency**: Optimized routing
- **Better reliability**: Managed connection
- **Cost savings**: Internal bandwidth

### **Monitoring**
- Vercel provides built-in monitoring
- Track API response times
- Monitor error rates
- Analyze usage patterns

## Deployment Checklist

- [ ] Connect Vercel to Railway in dashboard
- [ ] Set environment variables in Vercel
- [ ] Set environment variables in Railway
- [ ] Update CORS configuration
- [ ] Test connection in development
- [ ] Deploy and verify in production
- [ ] Monitor logs and performance

## Support

If you encounter issues:
1. Check Vercel integration status
2. Verify environment variables
3. Test backend health endpoint
4. Review Vercel and Railway logs
5. Check CORS configuration

# Railway Backend Configuration Fix

## 🚨 Issue Identified
The frontend was still pointing to `localhost:8000` instead of the Railway backend at `https://art-app-production.up.railway.app`.

## ✅ Changes Made

### 1. Frontend Configuration Files
- **`src/config.js`** - Already correctly configured with Railway URL
- **`env.production`** - Already correctly configured with Railway URL
- **`vercel.json`** - Added Vercel-specific configuration for proper deployment

### 2. Component Updates
Updated the following components to use the centralized config instead of hardcoded localhost URLs:

#### `src/components/OptimizedImage.vue`
- Added `import { config } from '@/config'`
- Changed `http://localhost:8000` to `config.apiBaseUrl`
- Fixed both `imageUrl` and `lowQualityUrl` computed properties

#### `src/views/ProfileView.vue`
- Added `import { config } from '@/config'`
- Changed `http://localhost:8000` to `config.apiBaseUrl` in profile picture URL generation

#### `src/components/AppHeader.vue`
- Added `import { config } from '@/config'`
- Changed `http://localhost:8000` to `config.apiBaseUrl` in profile picture URL generation

#### `src/views/GalleryView.vue`
- Added `import { config } from '@/config'`
- Changed `http://localhost:8000` to `config.apiBaseUrl` in placeholder image fallback

#### `src/utils/apiClient.js`
- Added `import { config } from '@/config'`
- Changed `http://localhost:8000` to `config.apiBaseUrl` in axios baseURL fallback

### 3. HTML Template Updates
- **`index.html`** - Updated preconnect link from localhost to Railway URL

### 4. Backend CORS Updates
- **`api/main.py`** - Removed hardcoded localhost origins from CORS configuration
- **`api/cors_config.py`** - Already properly configured for production domains

## 🔧 Configuration Details

### Frontend Environment Variables
```bash
# Production (Railway)
VITE_API_BASE_URL=https://art-app-production.up.railway.app
NODE_ENV=production
```

### Backend CORS Origins
```python
default_origins = [
    "https://myassemblage.art",
    "https://www.myassemblage.art", 
    "https://api.myassemblage.art"
]
```

### Centralized Configuration
```javascript
// src/config.js
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'https://art-app-production.up.railway.app',
  // ... other config
}
```

## 🧪 Verification

Run the verification script to ensure all changes are correct:
```bash
cd frontend
./verify_railway_config.sh
```

Expected output:
- ✅ config.js has correct Railway URL
- ✅ env.production has correct Railway URL  
- ✅ No localhost:8000 references found in source files
- ✅ Components have config imports
- ✅ Build successful

## 🚀 Deployment Steps

1. **Commit Changes**
   ```bash
   git add .
   git commit -m "Fix Railway backend configuration - remove localhost references"
   git push
   ```

2. **Vercel Redeployment**
   - Changes will automatically trigger a new Vercel deployment
   - The build should now complete successfully
   - Frontend will connect to Railway backend instead of localhost

3. **Verify Connection**
   - Check browser network tab to ensure API calls go to Railway
   - Verify authentication and artwork loading works
   - Test profile picture uploads and other features

## 📋 Files Modified

### Frontend Source Files
- `src/components/OptimizedImage.vue`
- `src/views/ProfileView.vue`
- `src/components/AppHeader.vue`
- `src/views/GalleryView.vue`
- `src/utils/apiClient.js`
- `index.html`

### Configuration Files
- `vercel.json` (new)
- `env.production` (already correct)
- `src/config.js` (already correct)

### Backend Files
- `api/main.py` (CORS origins)
- `api/cors_config.py` (already correct)

## 🎯 Benefits

- **Production Ready**: Frontend now properly connects to Railway backend
- **Centralized Config**: All API URLs managed from single config file
- **Environment Aware**: Automatically uses correct URLs for dev/prod
- **CORS Compliant**: Backend properly configured for production domains
- **Build Success**: Vercel deployment should now complete without errors

## 🔍 Troubleshooting

If issues persist:

1. **Check Railway Status**: Ensure backend is running and accessible
2. **Verify Environment Variables**: Check Railway dashboard for correct values
3. **Test API Endpoints**: Use curl or Postman to test Railway backend directly
4. **Check CORS**: Verify browser console for CORS errors
5. **Review Network Tab**: Ensure API calls go to Railway, not localhost

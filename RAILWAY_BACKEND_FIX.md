# Railway Backend Fix - Resolved 502 Errors

## Problem Summary
The Railway backend was getting 502 errors due to import path issues when running in the Docker container. The error was:

```
ModuleNotFoundError: No module named 'api.database'
```

## Root Cause
The issue was that when running in the Docker container:
1. The working directory is `/app`
2. The application code is in `/app/api/`
3. But the import statements were trying to import from `api.database.models` which would resolve to `/app/api/database/models`
4. However, the actual path structure is `/app/database/models`

## Additional Issue: CORS Middleware Import Failure
After fixing the import paths, a second issue emerged:
- The `get_cors_middleware()` function was being called immediately when the module was imported
- If the import failed, the function call would fail with an error
- This caused the application to crash during startup

## Build Issue: Complex Multi-stage Dockerfile
The original `Dockerfile.backend` was a complex multi-stage build that was failing during the build process:
- Issues with copying Python packages between stages
- Complex dependency management that could fail silently
- More points of failure during the build process

## CORS Configuration Issue
The external `cors_config.py` file was causing import errors during startup:
- Complex import fallbacks that could fail
- Dependency on external files that might not be available
- Unnecessary complexity for a simple CORS setup

## Fixes Applied

### 1. Switched to Simple Dockerfile
- **Before**: Complex multi-stage `Dockerfile.backend` with potential build issues
- **After**: Simple, reliable `Dockerfile.backend.simple` that's easier to debug and maintain

### 2. Updated Dockerfile.backend.simple
- **Before**: Basic Python setup without proper Railway configuration
- **After**: Full Railway configuration with proper port handling, health checks, and Python path setup

### 3. Fixed Python Path Configuration
- **Before**: `ENV PYTHONPATH=/app:/app/api` (complex)
- **After**: `ENV PYTHONPATH=/app` (simple and reliable)

### 4. Updated Import Handling in main.py
- **Before**: Complex fallback imports with multiple try-catch blocks
- **After**: Simple production imports that work reliably in the container

### 5. Simplified CORS Configuration
- **Before**: Complex import fallbacks and external file dependencies
- **After**: Direct CORS configuration using Railway environment variables
- **Benefits**: 
  - No external file dependencies
  - Uses Railway's built-in environment variable system
  - Easier to debug and maintain
  - More reliable startup

### 6. Fixed Port Configuration
- Ensured the application properly reads Railway's `PORT` environment variable
- Updated health check to use the correct port

## Current Configuration

### Dockerfile.backend.simple
```dockerfile
# Key features:
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1
CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
```

### main.py
```python
# Simplified import handling:
from api.database.models import User, UserLike, UserRating, UserNote, Board, BoardArtwork, Artwork
from api.database.config import get_db, init_db, test_connection
from api.schemas import (
    UserCreate, UserResponse, UserUpdate, UserLikeCreate, UserRatingCreate, 
    UserNoteCreate, BoardCreate, BoardResponse, BoardUpdate, BoardArtworkCreate,
    ArtworkResponse, Token
)
from api.services import UserService
from api.auth import get_current_user, create_access_token, get_password_hash

# Simplified CORS configuration using Railway environment variables:
cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

default_origins = [
    "https://myassemblage.art",
    "https://www.myassemblage.art",
    "http://localhost:3000",
    "http://localhost:5173"
]

all_origins = cors_origins + default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### railway.json
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "docker/Dockerfile.backend.simple"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5,
    "numReplicas": 1
  }
}
```

## Railway Environment Variables

Set these in your Railway dashboard:

```bash
# Required
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production

# Optional (will use defaults if not set)
CORS_ORIGINS=https://myassemblage.art,https://www.myassemblage.art
```

## Why This Approach is Better

1. **Simpler Build Process**: Single-stage build reduces points of failure
2. **Easier Debugging**: Simpler structure makes it easier to identify issues
3. **More Reliable**: Fewer complex operations that could fail during build
4. **Faster Builds**: No multi-stage copying or complex dependency management
5. **Better Maintainability**: Easier to understand and modify
6. **Railway Native**: Uses Railway's built-in environment variable system
7. **No External Dependencies**: CORS configuration is self-contained
8. **Predictable Imports**: Simple import paths that work reliably

## Verification
Run the verification script to ensure everything is configured correctly:
```bash
./scripts/verify_railway_config.sh
```

## Debug Tools
- `scripts/test_simple_startup.py` - Test simplified startup without complex imports
- `scripts/verify_railway_config.sh` - Configuration verification

## Deployment Steps
1. Commit changes: `git add . && git commit -m 'Simplify CORS configuration and use Railway environment variables'`
2. Push to repository: `git push origin main`
3. Railway will automatically redeploy
4. Monitor logs: `railway logs`

## Expected Result
After deployment, the backend should:
- ✅ Build successfully without Docker build errors
- ✅ Start successfully without import errors
- ✅ Start successfully without CORS middleware errors
- ✅ Use Railway environment variables for configuration
- ✅ Listen on the correct port (Railway's PORT or 8000)
- ✅ Respond to health checks at `/health`
- ✅ Handle all API requests properly

## If Issues Persist
1. Check Railway logs immediately after deployment
2. Verify environment variables in Railway dashboard
3. Test health endpoint: `curl https://your-app.railway.app/health`
4. Check if the app is listening on the correct port
5. Use debug scripts to test simplified startup
6. Verify Railway environment variables are set correctly

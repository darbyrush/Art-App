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

## Fixes Applied

### 1. Switched to Simple Dockerfile
- **Before**: Complex multi-stage `Dockerfile.backend` with potential build issues
- **After**: Simple, reliable `Dockerfile.backend.simple` that's easier to debug and maintain

### 2. Updated Dockerfile.backend.simple
- **Before**: Basic Python setup without proper Railway configuration
- **After**: Full Railway configuration with proper port handling, health checks, and Python path setup

### 3. Fixed Python Path Configuration
- **Added**: `ENV PYTHONPATH=/app:/app/api`
- This ensures that both the root directory and api directory are in the Python path
- Allows imports to work correctly from both locations

### 4. Updated Import Handling in main.py
- Added robust import fallbacks that try production paths first, then development paths
- Production paths: `from api.database.models import ...`
- Development paths: `from database.models import ...`

### 5. Fixed CORS Middleware Issue
- **Before**: Direct call to `get_cors_middleware()` that could fail
- **After**: Robust CORS configuration with multiple fallbacks:
  1. Try external CORS config from `api.cors_config`
  2. Try local CORS config from `cors_config`
  3. Fallback to basic CORS configuration if both fail

### 6. Fixed Port Configuration
- Ensured the application properly reads Railway's `PORT` environment variable
- Updated health check to use the correct port

## Current Configuration

### Dockerfile.backend.simple
```dockerfile
# Key features:
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app:/app/api
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1
CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
```

### main.py
```python
# Import handling:
try:
    # Production imports (when running in container)
    from api.database.models import User, UserLike, UserRating, UserNote, Board, BoardArtwork, Artwork
    # ... other imports
except ImportError:
    try:
        # Development imports (when running locally)
        from database.models import User, UserLike, UserRating, UserNote, Board, BoardArtwork, Artwork
        # ... other imports
    except ImportError as e:
        logging.error(f"❌ All import attempts failed: {e}")
        raise

# CORS middleware with robust fallbacks:
try:
    from api.cors_config import get_cors_middleware
    app.add_middleware(get_cors_middleware())
    logger.info("✅ Using external CORS configuration")
except ImportError:
    try:
        from cors_config import get_cors_middleware
        app.add_middleware(get_cors_middleware())
        logger.info("✅ Using local CORS configuration")
    except ImportError:
        # Final fallback: use basic CORS configuration
        logger.warning("⚠️ External CORS config not available, using basic CORS")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://myassemblage.art",
                "https://www.myassemblage.art",
                "http://localhost:3000",
                "http://localhost:5173"
            ],
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

## Why Dockerfile.backend.simple is Better

1. **Simpler Build Process**: Single-stage build reduces points of failure
2. **Easier Debugging**: Simpler structure makes it easier to identify issues
3. **More Reliable**: Fewer complex operations that could fail during build
4. **Faster Builds**: No multi-stage copying or complex dependency management
5. **Better Maintainability**: Easier to understand and modify

## Verification
Run the verification script to ensure everything is configured correctly:
```bash
./scripts/verify_railway_config.sh
```

## Debug Tools
- `scripts/debug_container.py` - Test imports in container environment
- `scripts/test_container_imports.py` - Comprehensive import testing
- `scripts/verify_railway_config.sh` - Configuration verification

## Deployment Steps
1. Commit changes: `git add . && git commit -m 'Fix Railway deployment configuration'`
2. Push to repository: `git push origin main`
3. Railway will automatically redeploy
4. Monitor logs: `railway logs`

## Expected Result
After deployment, the backend should:
- ✅ Build successfully without Docker build errors
- ✅ Start successfully without import errors
- ✅ Start successfully without CORS middleware errors
- ✅ Listen on the correct port (Railway's PORT or 8000)
- ✅ Respond to health checks at `/health`
- ✅ Handle all API requests properly

## If Issues Persist
1. Check Railway logs immediately after deployment
2. Verify environment variables in Railway dashboard
3. Test health endpoint: `curl https://your-app.railway.app/health`
4. Check if the app is listening on the correct port
5. Use debug scripts to test imports in container environment
6. Verify the build process completes successfully

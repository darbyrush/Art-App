# Art Explorer - Project Structure

## 🏗️ **Refactored Project Structure**

```
art-explorer/
├── README.md                           # Main project documentation
├── requirements.txt                    # Python dependencies
├── .env                               # Environment variables
├── .gitignore                         # Git ignore rules
│
├── app/                               # Main application
│   ├── __init__.py
│   ├── main.py                        # Streamlit main app (entry point)
│   └── config.py                      # App configuration
│
├── api/                               # FastAPI Backend
│   ├── __init__.py
│   ├── main.py                        # FastAPI app
│   ├── auth.py                        # Authentication logic
│   ├── schemas.py                     # Pydantic models
│   ├── services.py                    # Business logic
│   └── artwork_populator.py           # External API integration
│
├── database/                          # Database layer
│   ├── __init__.py
│   ├── config.py                      # Database configuration
│   ├── models.py                      # SQLAlchemy models
│   └── migrations/                    # Database migrations
│
├── frontend/                          # Frontend components
│   ├── __init__.py
│   ├── components/                    # Reusable UI components
│   │   ├── __init__.py
│   │   ├── auth.py                    # Authentication UI
│   │   ├── gallery.py                 # Gallery UI
│   │   └── artwork.py                 # Artwork display UI
│   ├── api_client.py                  # API communication
│   ├── auth_api.py                    # API-based authentication
│   └── utils.py                       # Frontend utilities
│
├── backend/                           # Legacy backend (for external APIs)
│   ├── __init__.py
│   ├── config.py                      # Backend configuration
│   ├── registry.py                    # Source registry
│   ├── metadata.py                    # Metadata processing
│   ├── utils.py                       # Backend utilities
│   └── services/
│       └── fetchers/                  # External API fetchers
│           ├── __init__.py
│           ├── cleveland.py
│           ├── smithsonian.py
│           ├── met.py
│           ├── harvard.py
│           ├── national_gallery.py
│           ├── walters.py
│           └── random_art.py
│
├── pages/                             # Streamlit pages
│   ├── 1_gallery.py                   # Gallery page
│   └── 2_admin.py                     # Admin page (future)
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_api.py                    # API tests
│   ├── test_database.py               # Database tests
│   ├── test_frontend.py               # Frontend tests
│   └── test_integration.py            # Integration tests
│
├── scripts/                           # Utility scripts
│   ├── populate_db.py                 # Database population
│   ├── setup_database.py              # Database setup
│   └── test_full_api.py               # Full API testing
│
├── docker/                            # Docker configuration
│   ├── Dockerfile                     # Main Dockerfile
│   └── docker-compose.yml             # Docker Compose
│
└── docs/                              # Documentation
    ├── API.md                         # API documentation
    ├── DATABASE.md                    # Database documentation
    └── DEPLOYMENT.md                  # Deployment guide
```

## 🔄 **Migration Steps**

### **Phase 1: File Organization**
1. Move test files to `tests/` directory
2. Move utility scripts to `scripts/` directory
3. Consolidate duplicate files
4. Create proper `__init__.py` files

### **Phase 2: Code Refactoring**
1. Separate concerns (frontend/backend/database)
2. Create reusable components
3. Standardize imports
4. Remove duplicate code

### **Phase 3: Documentation**
1. Update README files
2. Create API documentation
3. Add deployment guides
4. Document configuration

## 📋 **File Migration Map**

### **Files to Move:**
- `test_*.py` → `tests/`
- `populate_db.py` → `scripts/`
- `setup_database.py` → `scripts/`
- `debug_api.py` → `scripts/`
- `test_full_api.py` → `scripts/`
- `test_db.py` → `tests/`
- `test_service.py` → `tests/`

### **Files to Consolidate:**
- `app.py` + `app_api.py` → `app/main.py`
- `frontend/auth.py` + `frontend/auth_api.py` → `frontend/components/auth.py`

### **Files to Create:**
- `app/config.py` (app configuration)
- `frontend/components/` (UI components)
- `docs/` (documentation)
- `docker/` (Docker files)

## 🎯 **Benefits of Refactoring**

1. **Clear Separation of Concerns**: Frontend, backend, and database are clearly separated
2. **Maintainability**: Easier to find and modify code
3. **Scalability**: Better structure for adding new features
4. **Testing**: Organized test suite
5. **Documentation**: Clear documentation structure
6. **Deployment**: Proper Docker configuration

## 🚀 **Next Steps**

1. Create new directory structure
2. Move files to appropriate locations
3. Update imports and references
4. Test all functionality
5. Update documentation
6. Deploy refactored application 
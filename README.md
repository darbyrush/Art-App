# Art Explorer App

A modern Vue.js application that allows users to browse and rate artworks from various museum APIs with an Instagram-style interface.

## Features

- 🎨 **Instagram-style artwork browsing** with double-tap to like
- 🔐 **User authentication** with login/register
- 🖼️ **Personal gallery** of liked artworks
- 📊 **User statistics** and profile management
- 🎯 **Museum source filtering** for diverse art discovery
- ⭐ **Artwork rating system** (1-5 stars)
- 📱 **Responsive design** for all devices
- 🎭 **Modern UI/UX** with smooth animations
- 🚀 **Fast performance** with Vite and optimized builds

## Setup

### 1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys:

```env
# Smithsonian Institution API Key (Required)
# Get your free API key from: https://api.data.gov/signup/
SMITHSONIAN_API_KEY=your_smithsonian_api_key_here

# Metropolitan Museum of Art API Key (Optional)
# Get your API key from: https://metmuseum.github.io/
MET_API_KEY=your_met_api_key_here

# Harvard Art Museums API Key (Optional)
# Get your API key from: https://github.com/harvardartmuseums/api-docs
HARVARD_API_KEY=your_harvard_api_key_here

# Cleveland Museum of Art API Key (Optional)
CLEVELAND_API_KEY=your_cleveland_api_key_here
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Run the Application

**Start the Backend API:**
```bash
# From the root directory
uvicorn api.main:app --reload --port 8000
```

**Start the Frontend:**
```bash
# From the frontend directory
cd frontend
npm run dev
```

The application will be available at:
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`

## Tech Stack

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Tailwind CSS** - Utility-first CSS framework
- **Pinia** - State management for Vue
- **Vue Router** - Client-side routing
- **Axios** - HTTP client for API communication
- **Vite** - Fast build tool and dev server

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Uvicorn** - ASGI server

## API Key Sources

### Smithsonian Institution (Required)
- **URL**: https://api.data.gov/signup/
- **Cost**: Free
- **Rate Limit**: 1000 requests per hour

### Metropolitan Museum of Art (Optional)
- **URL**: https://metmuseum.github.io/
- **Cost**: Free
- **Rate Limit**: 80 requests per minute

### Harvard Art Museums (Optional)
- **URL**: https://github.com/harvardartmuseums/api-docs
- **Cost**: Free
- **Rate Limit**: 1000 requests per day

### Cleveland Museum of Art (Optional)
- **URL**: https://openaccess-api.clevelandart.org/
- **Cost**: Free
- **Rate Limit**: No limit specified

## Security

- API keys are stored in environment variables
- The `.env` file is ignored by git
- Never commit API keys to version control
- Use different API keys for development and production

## Features

### Multi-Source Selection
- Choose from multiple art sources
- Combine results from different museums
- Filter by specific sources

### Performance Monitoring
- Cache hit rate tracking
- Average fetch time monitoring
- Request count statistics
- Cache management tools

### Gallery Management
- Save liked artworks
- Add personal notes and ratings
- Export collections
- Browse your personal gallery

## Troubleshooting

### Missing API Keys
If you see ❌ next to a source in the sidebar, you need to add the corresponding API key to your `.env` file.

### Rate Limiting
If you encounter rate limiting errors, the app will automatically retry with exponential backoff.

### Cache Issues
Use the "Clear Cache" button in the sidebar to reset the cache if you encounter issues.

## Development

### Frontend Development
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`
4. Build for production: `npm run build`

### Backend Development
1. Install Python dependencies: `pip install -r requirements.txt`
2. Start the API server: `uvicorn api.main:app --reload --port 8000`
3. Access API documentation: `http://localhost:8000/docs`

### Adding New Sources
1. Create a new fetcher in `backend/services/fetchers/`
2. Add the API key configuration in `backend/config.py`
3. Update the registry in `backend/registry.py`

### Performance Optimization
- The app uses caching to reduce API calls
- Requests are made with timeouts and retry logic
- Performance statistics are tracked in real-time
- Frontend uses Vite for fast development and optimized builds 
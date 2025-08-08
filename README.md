# 🎨 Art Explorer

A modern, robust art discovery application that connects users with artworks from major museums around the world. Built with FastAPI, Vue.js, and SQLAlchemy.

## ✨ Features

### 🖼️ Art Discovery
- **Infinite Scroll**: Smooth pagination with improved scroll position preservation
- **Multi-Source Artworks**: Artworks from 7+ major museums
- **Smart Caching**: Efficient image and API response caching
- **Image Validation**: Automatic detection and replacement of broken image URLs

### 👤 User Experience
- **Personal Gallery**: Save and organize your favorite artworks
- **Rating System**: Rate artworks with 1-5 stars
- **Like/Unlike**: Simple one-click interactions
- **User Profiles**: Track your art exploration journey

### 🏛️ Museum Sources
- Metropolitan Museum of Art (Met)
- Cleveland Museum of Art
- Art Institute of Chicago
- Harvard Art Museums
- Smithsonian American Art Museum
- National Gallery of Art
- Walters Art Museum

### 🔧 Technical Improvements
- **Robust Error Handling**: Comprehensive error catching and logging
- **Image Fallbacks**: Automatic placeholder generation for broken images
- **Scalable Architecture**: Better handling of multiple concurrent users
- **Performance Optimization**: Efficient database queries and caching
- **Mobile Responsive**: Optimized for all device sizes

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16.0+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Art-App
   ```

2. **Run the deployment script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Start the application**
   ```bash
   ./start_app.sh
   ```

### Manual Setup

#### Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Initialize database
cd api
python -c "from database.config import init_db; init_db()"

# Populate with artworks
python -c "from api.artwork_populator import populate_database; populate_database()"

# Start backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Management Tools

### Image Validation
```bash
# Validate and fix broken image URLs
python scripts/validate_images.py
```

### Database Management
```bash
# Populate database with new artworks
python -c "from api.artwork_populator import populate_database; populate_database()"

# Get database statistics
curl http://localhost:8000/admin/database-stats
```

### Health Monitoring
```bash
# Check application health
curl http://localhost:8000/health

# Test CORS configuration
curl http://localhost:8000/cors-debug
```

## 🛠️ Architecture

### Backend (FastAPI)
- **API Layer**: RESTful endpoints with comprehensive error handling
- **Service Layer**: Business logic with improved error handling and logging
- **Data Layer**: SQLAlchemy ORM with optimized queries
- **Background Tasks**: Automated database population and cleanup
- **Image Processing**: Async image validation and placeholder generation

### Frontend (Vue.js)
- **Component Architecture**: Modular, reusable components
- **State Management**: Pinia stores for artwork and user data
- **Infinite Scroll**: Improved pagination with scroll position preservation
- **Image Handling**: Smart fallbacks and loading states
- **Responsive Design**: Mobile-first approach

### Database (SQLite)
- **User Management**: Authentication and user preferences
- **Artwork Storage**: Comprehensive artwork metadata
- **User Interactions**: Likes, ratings, and notes
- **Caching**: API response caching for performance

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password encryption
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive request validation
- **Error Sanitization**: Safe error responses

## 📊 Performance Optimizations

### Backend
- **Database Indexing**: Optimized queries with proper indexing
- **Connection Pooling**: Efficient database connection management
- **Async Operations**: Non-blocking image validation and API calls
- **Caching Strategy**: Multi-level caching for improved response times

### Frontend
- **Lazy Loading**: Images and components loaded on demand
- **Virtual Scrolling**: Efficient rendering of large lists
- **Image Optimization**: Automatic resizing and compression
- **Bundle Splitting**: Optimized JavaScript bundle sizes

## 🐛 Bug Fixes & Improvements

### Fixed Issues
1. **Scroll-to-Top Problem**: Infinite scroll now preserves scroll position
2. **404 Image Errors**: Automatic detection and replacement of broken images
3. **Rating System**: Enhanced error handling and validation
4. **User Scaling**: Better handling of multiple concurrent users

### New Features
1. **Image Validation**: Async validation of image URLs
2. **Placeholder Generation**: Automatic placeholder images for broken URLs
3. **Enhanced Error Handling**: Comprehensive error catching and logging
4. **Performance Monitoring**: Health checks and statistics endpoints
5. **Deployment Scripts**: Automated setup and deployment

## 🔄 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /token` - User login
- `GET /users/me` - Get current user

### Artworks
- `GET /artworks/random` - Get random artwork
- `GET /artworks/gallery` - Get paginated artworks
- `GET /artworks/search` - Search artworks
- `GET /artworks/recommendations` - Get personalized recommendations

### User Interactions
- `POST /artworks/{id}/like` - Like/unlike artwork
- `POST /artworks/{id}/rate` - Rate artwork
- `POST /artworks/{id}/note` - Add note to artwork
- `GET /users/me/likes` - Get user's liked artworks

### Admin
- `POST /admin/populate-database` - Populate database
- `GET /admin/database-stats` - Get database statistics
- `POST /admin/cleanup` - Clean up old artworks

### Utilities
- `GET /health` - Health check
- `GET /placeholder/{source}.jpg` - Placeholder images
- `GET /artworks/validate-images` - Validate image URLs

## 🧪 Testing

### Backend Tests
```bash
cd api
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Manual Testing
```bash
# Test image validation
python scripts/validate_images.py

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/test
```

## 📈 Monitoring

### Health Checks
- Database connectivity
- External API availability
- Image URL validation
- Background task status

### Performance Metrics
- Response times
- Database query performance
- Image loading times
- User interaction rates

## 🚀 Deployment

### Local Development
```bash
./start_app.sh
```

### Production Deployment
1. Set up environment variables
2. Configure database (PostgreSQL recommended)
3. Set up reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Museum APIs for providing artwork data
- FastAPI community for the excellent framework
- Vue.js team for the reactive frontend framework
- All contributors and users of this project

---

**Happy exploring! 🎨**

For support or questions, please open an issue on GitHub. 
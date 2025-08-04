# Art Explorer - Vue.js Frontend

A modern, responsive Vue.js frontend for the Art Explorer application with Tailwind CSS styling.

## Features

- 🎨 **Instagram-style artwork browsing** with double-tap to like
- 🔐 **User authentication** with login/register
- 🖼️ **Personal gallery** of liked artworks
- 📊 **User statistics** and profile management
- 🎯 **Museum source filtering** for diverse art discovery
- ⭐ **Artwork rating system** (1-5 stars)
- 📱 **Responsive design** for all devices
- 🎭 **Modern UI/UX** with smooth animations

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **Vue Router** - Official router for Vue.js
- **Pinia** - State management for Vue
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication
- **Vite** - Fast build tool and dev server

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to http://localhost:3000

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable Vue components
│   ├── views/         # Page components
│   ├── stores/        # Pinia state management
│   ├── utils/         # Utility functions
│   ├── assets/        # Static assets
│   ├── App.vue        # Root component
│   ├── main.js        # Application entry point
│   ├── router/        # Vue Router configuration
│   └── style.css      # Global styles with Tailwind
├── public/            # Public assets
├── index.html         # HTML template
├── package.json       # Dependencies and scripts
├── vite.config.js     # Vite configuration
├── tailwind.config.js # Tailwind CSS configuration
└── postcss.config.js  # PostCSS configuration
```

## Key Features

### 🎨 Instagram-Style Interface
- Card-based artwork display
- Double-tap to like functionality
- Smooth animations and transitions
- Heart beat animation on like

### 🔐 Authentication
- JWT token-based authentication
- Automatic token refresh
- Protected routes
- Persistent login state

### 🖼️ Gallery Management
- View all liked artworks
- Grid layout with hover effects
- Responsive design for all screen sizes

### 📊 User Statistics
- Track liked artworks count
- Museum diversity metrics
- Rating and note statistics

### 🎯 Museum Source Filtering
- Select specific museums
- Combine multiple sources
- Real-time filtering

## API Integration

The frontend communicates with the FastAPI backend through the `apiClient` utility:

- **Authentication**: Login, register, token management
- **Artworks**: Random artwork fetching, liking, rating
- **User Data**: Profile, statistics, gallery
- **Error Handling**: Automatic 401 redirects, error messages

## Styling

### Tailwind CSS Classes
- Custom color palette with art-themed colors
- Responsive design utilities
- Animation classes for smooth interactions
- Custom component classes for consistency

### Custom Components
- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary action buttons
- `.card` - Card containers
- `.artwork-card` - Artwork display cards
- `.instagram-container` - Instagram-style containers

## Development

### Adding New Features
1. Create components in `src/components/`
2. Add routes in `src/router/index.js`
3. Create stores in `src/stores/` if needed
4. Update API client in `src/utils/apiClient.js`

### Styling Guidelines
- Use Tailwind utility classes
- Follow the established color palette
- Maintain responsive design
- Add smooth transitions for interactions

## Deployment

The Vue.js app can be deployed to any static hosting service:

- **Netlify**: Connect to Git repository
- **Vercel**: Automatic deployments
- **GitHub Pages**: Static site hosting
- **AWS S3**: Static website hosting

## Contributing

1. Follow Vue.js best practices
2. Use TypeScript for better type safety
3. Write unit tests for components
4. Maintain consistent code style
5. Update documentation for new features
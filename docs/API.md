# Art Explorer API Documentation

## Overview

The Art Explorer API is a FastAPI-based backend that provides authentication, artwork management, and user interaction features.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require a valid token in the Authorization header.

### Register User
```
POST /register
Content-Type: application/json

{
    "username": "string",
    "password": "string",
    "email": "string (optional)"
}
```

### Login
```
POST /token
Content-Type: application/x-www-form-urlencoded

username=string&password=string
```

Response:
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

## Artwork Endpoints

### Get Random Artwork
```
GET /artworks/random?source=string
Authorization: Bearer <token>
```

### Like/Dislike Artwork
```
POST /artworks/{artwork_id}/like
Authorization: Bearer <token>
Content-Type: application/json

{
    "liked": true
}
```

### Rate Artwork
```
POST /artworks/{artwork_id}/rate
Authorization: Bearer <token>
Content-Type: application/json

{
    "rating": 5
}
```

### Add Note to Artwork
```
POST /artworks/{artwork_id}/note
Authorization: Bearer <token>
Content-Type: application/json

{
    "note": "string"
}
```

## User Endpoints

### Get User Information
```
GET /users/me
Authorization: Bearer <token>
```

### Get User Likes
```
GET /users/me/likes
Authorization: Bearer <token>
```

### Get User Statistics
```
GET /users/me/stats
Authorization: Bearer <token>
```

## Search Endpoints

### Search Artworks
```
GET /artworks/search?source=string&artist=string&date_range=string
Authorization: Bearer <token>
```

## Admin Endpoints

### Populate Database
```
POST /admin/populate-database?artworks_per_source=5
Authorization: Bearer <token>
```

### Get Database Statistics
```
GET /admin/database-stats
Authorization: Bearer <token>
```

## Health Check

### Check API Health
```
GET /health
```

Response:
```json
{
    "status": "healthy",
    "timestamp": "2025-08-04T03:50:01.300484"
}
```

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
    "detail": "Not Found"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error"
}
```

## Data Models

### Artwork
```json
{
    "id": "string",
    "title": "string",
    "artist": "string",
    "date": "string",
    "origin": "string",
    "department": "string",
    "source": "string",
    "image_url": "string",
    "external_id": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### User
```json
{
    "id": "string",
    "username": "string",
    "email": "string",
    "created_at": "datetime",
    "is_active": "boolean"
}
```

### User Stats
```json
{
    "total_artworks": 0,
    "liked_artworks": 0,
    "unique_museums": 0,
    "avg_rating": 0.0
}
```

## External API Integration

The API integrates with multiple museum APIs:

- Cleveland Museum of Art
- Metropolitan Museum of Art
- Smithsonian American Art Museum
- Harvard Art Museums
- National Gallery of Art
- Walters Art Museum

Artworks are fetched from these sources and stored in the local database for faster access. 
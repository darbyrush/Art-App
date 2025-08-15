"""
Rate limiting and security middleware for Art Explorer API
Optimized for scaling to 50+ concurrent users
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import logging
from typing import Dict, Optional
import os
from api.cache import rate_limiter

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Rate limiting middleware for API endpoints"""
    
    def __init__(self):
        # Rate limit configurations
        self.rate_limits = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "auth": {"requests": 10, "window": 60},      # 10 auth attempts per minute
            "search": {"requests": 50, "window": 60},    # 50 searches per minute
            "upload": {"requests": 20, "window": 60},    # 20 uploads per minute
            "api": {"requests": 200, "window": 60},      # 200 API calls per minute
        }
        
        # IP-based rate limiting
        self.ip_limits = {"requests": 500, "window": 60}  # 500 requests per IP per minute
    
    def get_rate_limit_config(self, path: str) -> Dict[str, int]:
        """Get rate limit configuration for a specific path"""
        if path.startswith("/auth") or path.startswith("/login") or path.startswith("/register"):
            return self.rate_limits["auth"]
        elif path.startswith("/search") or path.startswith("/artworks") and "search" in path:
            return self.rate_limits["search"]
        elif path.startswith("/upload") or "profile_picture" in path:
            return self.rate_limits["upload"]
        elif path.startswith("/api"):
            return self.rate_limits["api"]
        else:
            return self.rate_limits["default"]
    
    def get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client"""
        # Try to get real IP address (handles proxies)
        client_ip = request.headers.get("X-Forwarded-For")
        if not client_ip:
            client_ip = request.headers.get("X-Real-IP")
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        
        # Clean up IP address (take first one if multiple)
        if client_ip and "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        return client_ip or "unknown"
    
    async def __call__(self, request: Request, call_next):
        """Process the request with rate limiting"""
        start_time = time.time()
        
        # Get client identifier
        client_id = self.get_client_identifier(request)
        path = request.url.path
        
        # Skip rate limiting for health checks and static files
        if path in ["/health", "/docs", "/openapi.json"] or path.startswith("/static"):
            response = await call_next(request)
            return response
        
        try:
            # Check IP-based rate limiting
            ip_key = f"ip_limit:{client_id}"
            if not rate_limiter.is_allowed(ip_key, self.ip_limits["requests"], self.ip_limits["window"]):
                logger.warning(f"IP rate limit exceeded for {client_id}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests from this IP address",
                        "retry_after": self.ip_limits["window"]
                    },
                    headers={"Retry-After": str(self.ip_limits["window"])}
                )
            
            # Check endpoint-specific rate limiting
            endpoint_config = self.get_rate_limit_config(path)
            endpoint_key = f"endpoint_limit:{client_id}:{path}"
            
            if not rate_limiter.is_allowed(endpoint_key, endpoint_config["requests"], endpoint_config["window"]):
                logger.warning(f"Endpoint rate limit exceeded for {client_id} on {path}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests to {path}",
                        "retry_after": endpoint_config["window"]
                    },
                    headers={"Retry-After": str(endpoint_config["window"])}
                )
            
            # Process the request
            response = await call_next(request)
            
            # Add rate limit headers
            remaining_ip = rate_limiter.get_remaining(ip_key, self.ip_limits["requests"], self.ip_limits["window"])
            remaining_endpoint = rate_limiter.get_remaining(endpoint_key, endpoint_config["requests"], endpoint_config["window"])
            
            response.headers["X-RateLimit-IP-Remaining"] = str(remaining_ip)
            response.headers["X-RateLimit-Endpoint-Remaining"] = str(remaining_endpoint)
            response.headers["X-RateLimit-IP-Reset"] = str(int(start_time + self.ip_limits["window"]))
            response.headers["X-RateLimit-Endpoint-Reset"] = str(int(start_time + endpoint_config["window"]))
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Continue without rate limiting if there's an error
            return await call_next(request)

class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self):
        self.blocked_user_agents = [
            "bot", "crawler", "spider", "scraper", "curl", "wget", "python-requests"
        ]
    
    async def __call__(self, request: Request, call_next):
        """Process the request with security checks"""
        user_agent = request.headers.get("User-Agent", "").lower()
        
        # Block suspicious user agents
        if any(blocked in user_agent for blocked in self.blocked_user_agents):
            logger.warning(f"Blocked suspicious user agent: {user_agent}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Access denied", "message": "Invalid user agent"}
            )
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

class PerformanceMiddleware:
    """Performance monitoring middleware"""
    
    def __init__(self):
        self.request_times: Dict[str, list] = {}
    
    async def __call__(self, request: Request, call_next):
        """Process the request with performance monitoring"""
        start_time = time.time()
        path = request.url.path
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log slow requests
        if response_time > 1.0:  # Log requests taking more than 1 second
            logger.warning(f"Slow request: {path} took {response_time:.2f}s")
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{response_time:.3f}"
        
        return response

# Global middleware instances
rate_limit_middleware = RateLimitMiddleware()
security_middleware = SecurityMiddleware()
performance_middleware = PerformanceMiddleware()

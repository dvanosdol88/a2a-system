"""Authentication and Rate Limiting Middleware for A2A System"""

import time
import functools
from datetime import datetime, timedelta
from collections import defaultdict
from flask import request, jsonify, g

from config.settings import Config
from database.db_manager import db


class AuthMiddleware:
    """Handles API authentication and authorization"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app"""
        self.app = app
        app.before_request(self.authenticate_request)
    
    def authenticate_request(self):
        """Authenticate incoming requests"""
        # Skip auth for health check
        if request.path == '/health':
            return None
        
        # Skip auth if disabled
        if not Config.ENABLE_AUTH:
            g.api_key_info = None
            return None
        
        # Get API key from header
        api_key = request.headers.get(Config.API_KEY_HEADER)
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key
        key_info = db.validate_api_key(api_key)
        if not key_info:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Store key info for request
        g.api_key_info = key_info
        g.start_time = time.time()
        
        return None
    
    def require_permission(self, permission):
        """Decorator to require specific permission"""
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                if not Config.ENABLE_AUTH:
                    return f(*args, **kwargs)
                
                if not g.get('api_key_info'):
                    return jsonify({'error': 'Authentication required'}), 401
                
                permissions = g.api_key_info.get('permissions', {})
                if permission not in permissions:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


class RateLimiter:
    """Handles rate limiting for API endpoints"""
    
    def __init__(self, app=None):
        self.app = app
        self.request_counts = defaultdict(list)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize rate limiter with Flask app"""
        self.app = app
        app.before_request(self.check_rate_limit)
        app.after_request(self.log_request)
    
    def check_rate_limit(self):
        """Check if request exceeds rate limit"""
        if not Config.RATE_LIMIT_ENABLED:
            return None
        
        # Skip rate limiting for health check
        if request.path == '/health':
            return None
        
        # Get identifier (API key or IP)
        if g.get('api_key_info'):
            identifier = f"key_{g.api_key_info['id']}"
            limit = g.api_key_info.get('rate_limit', Config.RATE_LIMIT_DEFAULT)
        else:
            identifier = f"ip_{request.remote_addr}"
            limit = Config.RATE_LIMIT_DEFAULT
        
        # Clean old requests (older than 1 minute)
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        self.request_counts[identifier] = [
            req_time for req_time in self.request_counts[identifier]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self.request_counts[identifier]) >= limit:
            return jsonify({
                'error': 'Rate limit exceeded',
                'limit': limit,
                'window': '1 minute'
            }), 429
        
        # Record request
        self.request_counts[identifier].append(now)
        
        return None
    
    def log_request(self, response):
        """Log request for monitoring"""
        if hasattr(g, 'start_time'):
            response_time = int((time.time() - g.start_time) * 1000)
            
            # Log to database
            db.log_request(
                api_key_id=g.api_key_info['id'] if g.get('api_key_info') else None,
                endpoint=request.path,
                method=request.method,
                ip_address=request.remote_addr,
                response_code=response.status_code,
                response_time_ms=response_time
            )
        
        return response


def create_initial_api_key():
    """Create an initial API key for testing"""
    api_key = db.create_api_key(
        name="Default API Key",
        permissions={
            "read": True,
            "write": True,
            "admin": False
        }
    )
    print(f"Created API key: {api_key}")
    print(f"Add this to your .env file: A2A_API_KEY={api_key}")
    return api_key
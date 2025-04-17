# app/gateway/middleware.py
from functools import wraps
from flask import request, g, jsonify, current_app
import jwt
from app.shared.exceptions import UnauthorizedException, TenantNotFoundException

def tenant_resolver():
    """Middleware to extract and validate tenant information"""
    @wraps(lambda x: x)
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            tenant_id = request.headers.get('X-Tenant-ID')
            
            if not tenant_id:
                return jsonify({"error": "Missing tenant identifier"}), 400
            
            # Verify tenant exists in your system
            from app.core.services.tenant_service import get_tenant_by_id
            tenant = get_tenant_by_id(tenant_id)
            
            if not tenant:
                raise TenantNotFoundException(f"Tenant {tenant_id} not found")
            
            # Store tenant info in Flask's g object for access in route handlers
            g.tenant_id = tenant_id
            g.tenant = tenant
            
            return f(*args, **kwargs)
        return decorated
    return wrapper


def jwt_auth_required():
    """Middleware to verify JWT token and extract user info"""
    @wraps(lambda x: x)
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                raise UnauthorizedException("Missing or invalid authorization token")
            
            token = auth_header.split(' ')[1]
            
            try:
                # Verify token with your JWT secret
                payload = jwt.decode(
                    token, 
                    current_app.config['JWT_SECRET_KEY'],
                    algorithms=['HS256']
                )
                
                # Store user info in Flask's g object
                g.user_id = payload.get('sub')
                g.user_roles = payload.get('roles', [])
                
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                raise UnauthorizedException("Token has expired")
            except jwt.InvalidTokenError:
                raise UnauthorizedException("Invalid token")
            
        return decorated
    return wrapper


def rate_limiter(max_requests=100, window_seconds=60):
    """Rate limiting middleware based on tenant and IP"""
    @wraps(lambda x: x)
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            tenant_id = g.tenant_id if hasattr(g, 'tenant_id') else 'anonymous'
            client_ip = request.remote_addr
            
            # This is a simple in-memory implementation
            # In production, use Redis or similar for distributed rate limiting
            cache_key = f"rate_limit:{tenant_id}:{client_ip}"
            
            # Implement rate limiting logic here
            # For a real implementation, check the counter for cache_key
            # If exceeded, return 429 Too Many Requests
            
            return f(*args, **kwargs)
        return decorated
    return wrapper
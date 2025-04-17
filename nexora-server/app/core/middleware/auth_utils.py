import logging
from functools import wraps
from flask import request
from app.core.services.auth_service import auth_service
from app.shared.exceptions import UnauthorizedException, BadRequestException

logger = logging.getLogger(__name__)

def get_token(f):
    """Decorator to extract and verify JWT token, storing tenant_id in request."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from Authorization header or auth_token cookie
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    logger.error(f"Invalid token type: {token_type}")
                    raise UnauthorizedException("Invalid token type")
                logger.debug(f"Extracted token from Authorization header")
            except ValueError:
                logger.error("Invalid Authorization header format")
                raise UnauthorizedException("Invalid Authorization header format")
        else:
            token = request.cookies.get("auth_token")
            if not token:
                logger.error("Authorization header or auth_token cookie is missing")
                raise UnauthorizedException("Authorization header or auth_token cookie is missing")
            logger.debug(f"Extracted token from auth_token cookie")
        
        # Verify token and extract tenant_id
        try:
            payload = auth_service.verify_token(token)
            tenant_id = payload.get("tenant_id")
            if not tenant_id:
                logger.error("Tenant ID missing in token payload")
                raise BadRequestException("Tenant ID missing in token")
            # Store tenant_id in request context
            request.tenant_id = tenant_id
            logger.debug(f"Verified token for tenant_id: {tenant_id}")
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise UnauthorizedException(f"Invalid token: {str(e)}")
        
        # Call the decorated function
        return f(*args, **kwargs)
    
    return decorated_function
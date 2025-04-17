import logging
from functools import wraps
from flask import request
from app.core.services.auth_service import auth_service
from app.shared.exceptions import UnauthorizedException

logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    raise UnauthorizedException("Invalid token type")
            except ValueError:
                raise UnauthorizedException("Invalid Authorization header format")
        else:
            token = request.cookies.get("auth_token")
            if not token:
                logger.debug("No token found in Authorization header or auth_token cookie")
                raise UnauthorizedException("Token is missing")
        
        try:
            payload = auth_service.verify_token(token)
            logger.debug(f"Token verified for user: {payload.get('sub')}")
            request.user = payload  # Attach payload to request for endpoint use
        except UnauthorizedException as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise
        return f(*args, **kwargs)
    return decorated
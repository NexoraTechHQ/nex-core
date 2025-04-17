import jwt
from datetime import datetime, timedelta
from flask import current_app
from app.core.database.pocketbase_client import PocketBaseClient
from app.shared.exceptions import BadRequestException, ConflictException, InternalServerException, UnauthorizedException, ForbiddenException
import requests
import logging

logger = logging.getLogger(__name__)

class AuthService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.pb = None
        self.secret_key = None
        
    def init_app(self, app):
        """Initialize with app context"""
        self.pb = PocketBaseClient(base_url=app.config['POCKETBASE_URL'])
        self.secret_key = app.config['SECRET_KEY']
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user with PocketBase and return token and tenant_id"""
        if not self.pb:
            raise RuntimeError("AuthService not initialized with app context")
        
        try:
            auth_data = self.pb.auth_with_password(username, password)
            if not auth_data:
                raise UnauthorizedException("Invalid credentials")
            
            user = auth_data['record']
            roles = ['admin'] if user.get('is_admin', False) else ['user']
            token = self.generate_jwt(
                user_id=user['id'],
                email=user['email'],
                tenant_id=user['tenant_id'],
                roles=roles,
                pb_token=auth_data['token']
            )
            return {
                'token': token,
                'tenant_id': user['tenant_id'],
                'user_id': user['id']
            }
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {str(e)}")
            raise UnauthorizedException("Invalid credentials")

    def generate_jwt(self, user_id: str, email: str, tenant_id: str, roles: list, pb_token: str = None) -> str:
        """Generate JWT token with custom claims"""
        payload = {
            'sub': user_id,
            'email': email,
            'tenant_id': tenant_id,
            'roles': roles,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS'])
        }
        if pb_token:
            payload['pb_token'] = pb_token
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str):
        """Verify JWT token and return payload"""
        if not self.secret_key:
            raise RuntimeError("AuthService not initialized with app context")
            
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Invalid token")
        
    def create_user(self, email: str, password: str, tenant_id: str, is_admin: bool, user_data: dict) -> dict:
        """Create a new user in PocketBase"""
        allowed_fields = ['name', 'contact_phone']
        filtered_user_data = {
            k: v for k, v in user_data.items()
            if k in allowed_fields
        }
        user_record = {
            'email': email,
            'password': password,
            'passwordConfirm': password,
            'emailVisibility': True,
            'tenant_id': tenant_id,
            'is_admin': is_admin,
            **filtered_user_data
        }
        
        logger.debug(f"Creating user with record: {user_record}")
        try:
            result = self.pb.collection('users').create(user_record)
            logger.debug(f"User created: {result}")
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                try:
                    error_details = e.response.json()
                    error_message = error_details.get('message', 'Unknown error')
                    error_data = error_details.get('data', {})
                    detailed_errors = '; '.join(
                        f"{field}: {err.get('message', 'Unknown error')}"
                        for field, err in error_data.items()
                    ) or error_message
                    logger.error(f"PocketBase 400 error: {error_message}, details: {error_data}")
                    raise BadRequestException(f"Invalid user data: {detailed_errors}")
                except ValueError:
                    logger.error(f"PocketBase 400 error without JSON: {str(e)}")
                    raise BadRequestException(f"Invalid user data: {str(e)}")
            elif e.response.status_code == 409 or "already exists" in str(e).lower():
                logger.error(f"User email conflict: {email}")
                raise ConflictException("User email already exists")
            logger.error(f"PocketBase error: {str(e)}")
            raise InternalServerException(f"Failed to create user: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating user: {str(e)}", exc_info=True)
            raise InternalServerException(f"Failed to create user: {str(e)}")
    
    def refresh_token(self, old_token: str):
        """Refresh expired token"""
        if not self.pb:
            raise RuntimeError("AuthService not initialized with app context")
            
        try:
            old_payload = jwt.decode(old_token, self.secret_key, algorithms=['HS256'], options={'verify_exp': False})
            
            # Refresh PocketBase token first
            pb_auth = self.pb.refresh_auth(old_payload['pb_token'])
            if not pb_auth:
                raise UnauthorizedException("Failed to refresh PocketBase token")
            
            # Generate new JWT with same claims but new expiration
            return self.generate_jwt(
                user_id=old_payload['sub'],
                email=old_payload['email'],
                tenant_id=old_payload['tenant_id'],
                roles=old_payload['roles'],
                pb_token=pb_auth['token']
            )
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Invalid token")

# Create singleton instance
auth_service = AuthService()
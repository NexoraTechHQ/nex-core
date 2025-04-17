import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from flask import Blueprint, current_app, request, jsonify
from app.core.middleware.auth_middleware import token_required
from app.core.services.auth_service import auth_service
from app.core.services.tenant_service import tenant_service
from app.shared.exceptions import (
    ConflictException,
    InternalServerException,
    handle_exceptions,
    BadRequestException,
    UnauthorizedException
)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
@handle_exceptions
def register():
    data = request.get_json()
    logger.debug(f"Received registration request: {data}")
    if not data or 'email' not in data or 'password' not in data:
        raise BadRequestException("Email and password are required")
    
    required_fields = {
        'individual': ['name'],
        'business': ['company_name', 'tax_id', 'contact_phone']
    }
    tenant_type = data.get('tenant_type', 'individual')
    for field in required_fields.get(tenant_type, []):
        if field not in data:
            raise BadRequestException(f"{field.replace('_', ' ').title()} is required for {tenant_type} registration")

    try:
        logger.debug(f"Creating tenant with type: {tenant_type}")
        tenant = tenant_service.create_tenant(tenant_type=tenant_type, tenant_data=data)
        logger.debug(f"Created tenant: {tenant}")
        logger.debug(f"Creating user with email: {data['email']}")
        user = auth_service.create_user(
            email=data['email'],
            password=data['password'],
            tenant_id=tenant['tenant_id'],
            is_admin=True,
            user_data=data
        )
        logger.debug(f"Created user: {user}")
        token = auth_service.generate_jwt(
            user_id=user['id'],
            email=user['email'],
            tenant_id=tenant['tenant_id'],
            roles=['admin'],
            pb_token=None
        )
        logger.debug("Generated JWT token")
        response = jsonify({
            'message': 'Registration successful',
            'tenant_id': tenant['tenant_id'],
            'user_id': user['id'],
            'token': token
        })
        response.status_code = 201
        # Set token in HTTP-only cookie
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite='Strict',
            max_age=int(current_app.config['JWT_EXPIRATION_HOURS'] * 3600)
        )
        return response
    except BadRequestException as e:
        logger.error(f"Bad request: {str(e)}", exc_info=True)
        raise
    except ConflictException as e:
        logger.error(f"Conflict: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        if "already exists" in str(e).lower():
            raise ConflictException("Email or tenant already registered")
        raise

@bp.route('/login', methods=['POST'])
@handle_exceptions
def login():
    data = request.get_json()
    logger.debug(f"Received login request: {data}")
    if not data or 'email' not in data or 'password' not in data:
        raise BadRequestException("Email and password are required")
    
    try:
        auth_result = auth_service.authenticate_user(
            username=data['email'],
            password=data['password']
        )
        logger.debug(f"Login successful for {data['email']}")
        response = jsonify({
            'message': 'Login successful',
            'token': auth_result['token'],
            'user_id': auth_result['user_id'],
            'tenant_id': auth_result['tenant_id']
        })
        # Set token in HTTP-only cookie
        response.set_cookie(
            'auth_token',
            auth_result['token'],
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite='Strict',
            max_age=int(current_app.config['JWT_EXPIRATION_HOURS'] * 3600)
        )
        return response
    except UnauthorizedException as e:
        logger.error(f"Login failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        raise InternalServerException("Failed to process login")

@bp.route('/refresh', methods=['POST'])
@handle_exceptions
def refresh():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise UnauthorizedException("Bearer token required")
    
    old_token = auth_header.split(' ')[1]
    new_token = auth_service.refresh_token(old_token)
    return jsonify({'token': new_token,
    })

@bp.route('/me', methods=['GET'])
@handle_exceptions
@token_required
def get_me():
    """Return details of the authenticated user"""
    user = request.user  # Payload from token_required
    logger.debug(f"Fetching user details for user_id: {user['sub']}")
    return jsonify({
        'user_id': user['sub'],
        'email': user['email'],
        'tenant_id': user['tenant_id'],
        'roles': user['roles']
    })
# app/shared/exceptions.py
from functools import wraps
from flask import jsonify

class BaseAPIException(Exception):
    """Base exception class for API errors"""
    status_code = 500
    message = "An unexpected error occurred"

    def __init__(self, message=None, status_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)

# Authentication / Authorization
class UnauthorizedException(BaseAPIException):
    status_code = 401
    message = "Unauthorized access"

class ForbiddenException(BaseAPIException):
    status_code = 403
    message = "Access forbidden"

# Request Errors
class BadRequestException(BaseAPIException):
    status_code = 400
    message = "Bad request"

class ValidationException(BaseAPIException):
    status_code = 400
    message = "Validation error"

class ConflictException(BaseAPIException):
    status_code = 409
    message = "Resource conflict"

class MethodNotAllowedException(BaseAPIException):
    status_code = 405
    message = "Method not allowed"

class UnprocessableEntityException(BaseAPIException):
    status_code = 422
    message = "Unprocessable entity"

# Not Found
class NotFoundException(BaseAPIException):
    status_code = 404
    message = "Resource not found"

class TenantNotFoundException(NotFoundException):
    message = "Tenant not found"

class ServiceNotFoundException(BaseAPIException):
    status_code = 503
    message = "Service unavailable"

# Rate Limiting
class RateLimitExceededException(BaseAPIException):
    status_code = 429
    message = "Too many requests"

# Server Errors
class InternalServerException(BaseAPIException):
    status_code = 500
    message = "Internal server error"

class GatewayTimeoutException(BaseAPIException):
    status_code = 504
    message = "Gateway timeout"

# Decorator for catching and returning consistent error responses
def handle_exceptions(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseAPIException as e:
            return jsonify({
                'error': e.message,
                'status_code': e.status_code
            }), e.status_code
        except Exception as e:
            return jsonify({
                'error': 'Internal server error',
                'details': str(e),
                'status_code': 500
            }), 500
    return decorated

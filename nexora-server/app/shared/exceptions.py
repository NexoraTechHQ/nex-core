# app/shared/exceptions.py

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


class UnauthorizedException(BaseAPIException):
    """Exception raised for authentication and authorization errors"""
    status_code = 401
    message = "Unauthorized access"


class ForbiddenException(BaseAPIException):
    """Exception raised when a user lacks permissions for a resource"""
    status_code = 403
    message = "Access forbidden"


class NotFoundException(BaseAPIException):
    """Exception raised when a resource is not found"""
    status_code = 404
    message = "Resource not found"


class TenantNotFoundException(NotFoundException):
    """Exception raised when a tenant is not found"""
    message = "Tenant not found"


class ServiceNotFoundException(BaseAPIException):
    """Exception raised when a service is not registered or unavailable"""
    status_code = 503
    message = "Service unavailable"


class RateLimitExceededException(BaseAPIException):
    """Exception raised when rate limit is exceeded"""
    status_code = 429
    message = "Too many requests"


class ValidationException(BaseAPIException):
    """Exception raised for data validation errors"""
    status_code = 400
    message = "Validation error"


class ConflictException(BaseAPIException):
    """Exception raised for resource conflicts (e.g., duplicate entries)"""
    status_code = 409
    message = "Resource conflict"


class GatewayTimeoutException(BaseAPIException):
    """Exception raised when a service request times out"""
    status_code = 504
    message = "Gateway timeout"
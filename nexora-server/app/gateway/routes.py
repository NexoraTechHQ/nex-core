# app/gateway/routes.py
from flask import Blueprint, request, g, jsonify
import requests
from urllib.parse import urljoin
import random
from .middleware import tenant_resolver, jwt_auth_required, rate_limiter
from app.shared.exceptions import ServiceNotFoundException

# Define service endpoints - in production, use service discovery
SERVICE_REGISTRY = {
    'inventory': {
        'instances': ['http://inventory-service:5001', 'http://inventory-service:5002'],
        'prefix': '/inventory'
    },
    'vms': {
        'instances': ['http://vms-service:5010', 'http://vms-service:5011'],
        'prefix': '/vms'
    },
    'access-control': {
        'instances': ['http://access-control-service:5020'],
        'prefix': '/access-control'
    }
}


def get_service_url(service_name):
    """Get a random service instance URL for load balancing"""
    if service_name not in SERVICE_REGISTRY:
        raise ServiceNotFoundException(f"Service {service_name} not registered")
    
    instances = SERVICE_REGISTRY[service_name]['instances']
    # Simple random load balancing
    return random.choice(instances)


def register_gateway_routes(bp: Blueprint):
    # Tenant health check endpoint
    @bp.route('/health', methods=['GET'])
    @tenant_resolver()
    def health_check():
        return jsonify({
            'status': 'ok',
            'tenant': g.tenant_id
        })

    # Route for inventory service
    @bp.route('/inventory/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    @tenant_resolver()
    @jwt_auth_required()
    @rate_limiter()
    def inventory_proxy(subpath):
        return proxy_request('inventory', subpath)
    
    # Route for VMS service
    @bp.route('/vms/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    @tenant_resolver()
    @jwt_auth_required()
    @rate_limiter()
    def vms_proxy(subpath):
        return proxy_request('vms', subpath)
    
    # Route for access control service
    @bp.route('/access-control/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    @tenant_resolver()
    @jwt_auth_required()
    @rate_limiter(max_requests=50)  # More strict rate limiting for security-related endpoints
    def access_control_proxy(subpath):
        return proxy_request('access-control', subpath)


def proxy_request(service_name, subpath):
    """Proxy the request to the underlying microservice"""
    service_url = get_service_url(service_name)
    
    # Build target URL
    target_path = f"{SERVICE_REGISTRY[service_name]['prefix']}/{subpath}"
    target_url = urljoin(service_url, target_path)
    
    # Forward the request with tenant information
    headers = {key: value for key, value in request.headers if key != 'Host'}
    headers['X-Tenant-ID'] = g.tenant_id
    
    if hasattr(g, 'user_id'):
        headers['X-User-ID'] = g.user_id
    
    try:
        # Make the proxied request
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            timeout=5  # Set a reasonable timeout
        )
        
        # Return the response from the service
        return resp.content, resp.status_code, resp.headers.items()
    except requests.RequestException as e:
        return jsonify({
            'error': 'Service unavailable',
            'service': service_name,
            'details': str(e)
        }), 503
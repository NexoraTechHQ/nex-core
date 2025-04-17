
from flask import Flask, jsonify
from app.inventory import register_inventory_routes
from app.gateway import register_gateway
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'dev-secret-key'),
        POCKETBASE_URL=os.environ.get('POCKETBASE_URL', 'http://localhost:8090'),
        ENVIRONMENT=os.environ.get('ENVIRONMENT', 'development')
    )
    
    # Register API Gateway (handles all tenant routing)
    register_gateway(app)
    
    # Register direct routes for internal use
    # In production, these should only be accessible internally
    register_inventory_routes(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500
    
    from app.shared.exceptions import (
        UnauthorizedException, 
        TenantNotFoundException,
        ServiceNotFoundException
    )
    
    @app.errorhandler(UnauthorizedException)
    def handle_unauthorized(e):
        return jsonify({"error": str(e)}), 401
    
    @app.errorhandler(TenantNotFoundException)
    def handle_tenant_not_found(e):
        return jsonify({"error": str(e)}), 404
    
    @app.errorhandler(ServiceNotFoundException)
    def handle_service_not_found(e):
        return jsonify({"error": str(e)}), 503
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
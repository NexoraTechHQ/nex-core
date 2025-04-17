# app/run.py
from flask import Flask
from flask_cors import CORS
from app.core.services.auth_service import auth_service

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration settings
    app.config['SECRET_KEY'] = 'fc55b68e4630141e255df3313b93bfe35569a3dd9af17d05d83df2791b0986f8'
    app.config['JWT_EXPIRATION_HOURS'] = 1
    app.config['POCKETBASE_URL'] = 'http://localhost:8090'
    
    # Initialize services
    auth_service.init_app(app)
    
    # Register blueprints
    from app.auth import register_auth_routes
    register_auth_routes(app)
    
    # Register inventory routes
    from app.inventory import register_inventory_routes
    register_inventory_routes(app)
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
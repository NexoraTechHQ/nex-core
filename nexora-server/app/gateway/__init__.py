# app/gateway/__init__.py
from flask import Blueprint, Flask
from .routes import register_gateway_routes

bp = Blueprint('gateway', __name__, url_prefix='/api')

def register_gateway(app: Flask):
    register_gateway_routes(bp)
    app.register_blueprint(bp)
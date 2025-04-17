#app/auth/__init__.py
from .api.auth import bp as auth_bp


def register_auth_routes(app):
    app.register_blueprint(auth_bp)


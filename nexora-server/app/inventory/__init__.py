from .api.roles import bp as roles_bp
from .api.departments import bp as departments_bp


def register_inventory_routes(app):
    app.register_blueprint(roles_bp)
    app.register_blueprint(departments_bp)

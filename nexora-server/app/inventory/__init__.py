from .api.roles import bp as roles_bp
from .api.departments import bp as departments_bp
from .api.permissions import bp as permissions_bp
from .api.tags import bp as tags_bp
from .api.rooms import bp as rooms_bp
from .api.visitors import bp as visitors_bp


def register_inventory_routes(app):
    app.register_blueprint(roles_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(permissions_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(visitors_bp)

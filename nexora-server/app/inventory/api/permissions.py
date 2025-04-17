import logging
from flask import Blueprint, request, jsonify
from app.core.schemas.permission import PermissionCreate, PermissionUpdate
from app.inventory.services.permission_service import permission_service
from app.core.middleware.auth_utils import get_token
from app.shared.exceptions import handle_exceptions

logger = logging.getLogger(__name__)

bp = Blueprint("permissions", __name__, url_prefix="/api/inventory/permissions")

@bp.route("/", methods=["GET"])
@handle_exceptions
@get_token
def list_permissions():
    """List permissions for the authenticated user's tenant with pagination and filtering"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(f"Listing permissions for tenant {tenant_id} with params: {query_params}")
    permissions = permission_service.list(query_params, tenant_id)
    return jsonify(permissions)

@bp.route("/<id>", methods=["GET"])
@handle_exceptions
@get_token
def get_permission(id):
    """Get a permission by ID for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(f"Fetching permission {id} for tenant {tenant_id} with params: {query_params}")
    permission = permission_service.get(id, tenant_id, query_params)
    return jsonify(permission)

@bp.route("/", methods=["POST"])
@handle_exceptions
@get_token
def create_permission():
    """Create a new permission for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    data = PermissionCreate(**request.get_json())
    query_params = request.args.to_dict()
    logger.debug(f"Creating permission for tenant {tenant_id}: {data} with params: {query_params}")
    permission = permission_service.create(data, tenant_id, query_params)
    return jsonify(permission), 201

@bp.route("/<id>", methods=["PUT"])
@handle_exceptions
@get_token
def update_permission(id):
    """Update a permission for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    data = PermissionUpdate(**request.get_json())
    query_params = request.args.to_dict()
    logger.debug(f"Updating permission {id} for tenant {tenant_id}: {data} with params: {query_params}")
    permission = permission_service.update(id, data, tenant_id, query_params)
    return jsonify(permission)

@bp.route("/<id>", methods=["DELETE"])
@handle_exceptions
@get_token
def delete_permission(id):
    """Delete a permission for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    logger.debug(f"Deleting permission {id} for tenant {tenant_id}")
    result = permission_service.delete(id, tenant_id)
    return jsonify(result)
import logging
from flask import Blueprint, request, jsonify
from app.core.schemas.role import RoleCreate, RoleUpdate
from app.inventory.services.role_service import role_service
from app.core.middleware.auth_utils import get_token
from app.shared.exceptions import handle_exceptions

logger = logging.getLogger(__name__)

bp = Blueprint("roles", __name__, url_prefix="/api/inventory/roles")

@bp.route("/", methods=["GET"])
@handle_exceptions
@get_token
def list_roles():
    """List roles for the authenticated user's tenant with pagination and filtering"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(f"Received query params for listing roles: {query_params}")
    logger.debug(f"Listing roles for tenant {tenant_id} with params: {query_params}")
    roles = role_service.list(query_params, tenant_id)
    return jsonify(roles)

@bp.route("/<id>", methods=["GET"])
@handle_exceptions
@get_token
def get_role(id):
    """Get a role by ID for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(f"Fetching role {id} for tenant {tenant_id} with params: {query_params}")
    role = role_service.get(id, tenant_id, query_params)
    return jsonify(role)

@bp.route("/", methods=["POST"])
@handle_exceptions
@get_token
def create_role():
    """Create a new role for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    data = RoleCreate(**request.get_json())
    query_params = request.args.to_dict()
    logger.debug(f"Creating role for tenant {tenant_id}: {data} with params: {query_params}")
    role = role_service.create(data, tenant_id, query_params)
    return jsonify(role), 201

@bp.route("/<id>", methods=["PUT"])
@handle_exceptions
@get_token
def update_role(id):
    """Update a role for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    data = RoleUpdate(**request.get_json())
    query_params = request.args.to_dict()
    logger.debug(f"Updating role {id} for tenant {tenant_id}: {data} with params: {query_params}")
    role = role_service.update(id, data, tenant_id, query_params)
    return jsonify(role)

@bp.route("/<id>", methods=["DELETE"])
@handle_exceptions
@get_token
def delete_role(id):
    """Delete a role for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    logger.debug(f"Deleting role {id} for tenant {tenant_id}")
    result = role_service.delete(id, tenant_id)
    return jsonify(result)
import logging
from flask import Blueprint, request, jsonify
from app.core.schemas.department import DepartmentCreate, DepartmentUpdate
from app.inventory.services.department_service import department_service
from app.core.middleware.auth_utils import get_token
from app.shared.exceptions import handle_exceptions

logger = logging.getLogger(__name__)

bp = Blueprint("departments", __name__, url_prefix="/api/inventory/departments")

@bp.route("/", methods=["GET"])
@handle_exceptions
@get_token
def list_departments():
    """List departments for the authenticated user's tenant with pagination and filtering"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(f"Listing departments for tenant {tenant_id} with params: {query_params}")
    departments = department_service.list(query_params, tenant_id)
    return jsonify(departments)

@bp.route("/<id>", methods=["GET"])
@handle_exceptions
@get_token
def get_department(id):
    """Get a department by ID for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(f"Fetching department {id} for tenant {tenant_id} with params: {query_params}")
    department = department_service.get(id, tenant_id, query_params)
    return jsonify(department)

@bp.route("/", methods=["POST"])
@handle_exceptions
@get_token
def create_department():
    """Create a new department for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    data = DepartmentCreate(**request.get_json())
    query_params = request.args.to_dict()
    logger.debug(f"Creating department for tenant {tenant_id}: {data} with params: {query_params}")
    department = department_service.create(data, tenant_id, query_params)
    return jsonify(department), 201

@bp.route("/<id>", methods=["PUT"])
@handle_exceptions
@get_token
def update_department(id):
    """Update a department for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    data = DepartmentUpdate(**request.get_json())
    query_params = request.args.to_dict()
    logger.debug(f"Updating department {id} for tenant {tenant_id}: {data} with params: {query_params}")
    department = department_service.update(id, data, tenant_id, query_params)
    return jsonify(department)

@bp.route("/<id>", methods=["DELETE"])
@handle_exceptions
@get_token
def delete_department(id):
    """Delete a department for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    logger.debug(f"Deleting department {id} for tenant {tenant_id}")
    result = department_service.delete(id, tenant_id)
    return jsonify(result)
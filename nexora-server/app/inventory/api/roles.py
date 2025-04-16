# inventory/api/roles.py
from flask import Blueprint, request, jsonify
from app.core.schemas.role import RoleCreate, RoleUpdate
from app.inventory.services.role_service import RoleService
from app.shared.utils.response import sanitize_response, error_response

bp = Blueprint("roles", __name__, url_prefix="/api/inventory/roles")


def get_tenant_id():
    return request.headers.get("X-Tenant-ID")


@bp.get("/")
def list_roles():
    try:
        tenant_id = get_tenant_id()
        roles = RoleService.list(request.args.to_dict(), tenant_id)
        return jsonify(sanitize_response(roles))
    except Exception as e:
        return error_response(f"Failed to fetch roles: {str(e)}", 400)


@bp.get("/<id>")
def get_role(id):
    try:
        tenant_id = get_tenant_id()
        role = RoleService.get(id, tenant_id)
        return jsonify(sanitize_response(role))
    except:
        return error_response("Role not found", 404)


@bp.post("/")
def create_role():
    try:
        tenant_id = get_tenant_id()
        data = RoleCreate(**request.json)
        role = RoleService.create(data, tenant_id)
        return jsonify(sanitize_response(role)), 201
    except Exception as e:
        return error_response(f"Failed to create role: {str(e)}", 400)


@bp.put("/<id>")
def update_role(id):
    try:
        tenant_id = get_tenant_id()
        data = RoleUpdate(**request.json)
        role = RoleService.update(id, data, tenant_id)
        return jsonify(sanitize_response(role))
    except Exception as e:
        return error_response(f"Failed to update role: {str(e)}", 400)


@bp.delete("/<id>")
def delete_role(id):
    try:
        tenant_id = get_tenant_id()
        return jsonify(RoleService.delete(id, tenant_id))
    except:
        return error_response("Role not found", 404)

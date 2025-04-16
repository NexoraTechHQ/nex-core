from flask import Blueprint, request, jsonify
from app.core.schemas.permission import PermissionCreate, PermissionUpdate
from app.inventory.services.permission_service import PermissionService
from app.shared.utils.response import sanitize_response, error_response

bp = Blueprint("permissions", __name__,
               url_prefix="/api/inventory/permissions")


def get_tenant_id():
    return request.headers.get("X-Tenant-ID")


@bp.get("/")
def list_permissions():
    try:
        tenant_id = get_tenant_id()
        permissions = PermissionService.list(request.args.to_dict(), tenant_id)
        return jsonify(sanitize_response(permissions))
    except Exception as e:
        return error_response(f"Failed to fetch permissions: {str(e)}", 400)


@bp.get("/<id>")
def get_permission(id):
    try:
        tenant_id = get_tenant_id()
        permission = PermissionService.get(id, tenant_id)
        return jsonify(sanitize_response(permission))
    except:
        return error_response("Permission not found", 404)


@bp.post("/")
def create_permission():
    try:
        tenant_id = get_tenant_id()
        data = PermissionCreate(**request.json)
        permission = PermissionService.create(data, tenant_id)
        return jsonify(sanitize_response(permission)), 201
    except Exception as e:
        return error_response(f"Failed to create permission: {str(e)}", 400)


@bp.put("/<id>")
def update_permission(id):
    try:
        tenant_id = get_tenant_id()
        data = PermissionUpdate(**request.json)
        permission = PermissionService.update(id, data, tenant_id)
        return jsonify(sanitize_response(permission))
    except Exception as e:
        return error_response(f"Failed to update permission: {str(e)}", 400)


@bp.delete("/<id>")
def delete_permission(id):
    try:
        tenant_id = get_tenant_id()
        return jsonify(PermissionService.delete(id, tenant_id))
    except:
        return error_response("Permission not found", 404)

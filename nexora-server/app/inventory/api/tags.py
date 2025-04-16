from flask import Blueprint, request, jsonify
from app.core.schemas.tag import TagCreate, TagUpdate
from app.inventory.services.tag_service import TagService
from app.shared.utils.response import sanitize_response, error_response

bp = Blueprint("tags", __name__, url_prefix="/api/inventory/tags")


def get_tenant_id():
    return request.headers.get("X-Tenant-ID")


@bp.get("/")
def list_tags():
    try:
        tenant_id = get_tenant_id()
        print('tenant_id', tenant_id)

        tags = TagService.list(request.args.to_dict(), tenant_id)
        return jsonify(sanitize_response(tags))
    except Exception as e:
        return error_response(f"Failed to fetch tags: {str(e)}", 400)


@bp.get("/<id>")
def get_tag(id):
    try:
        tenant_id = get_tenant_id()
        tag = TagService.get(id, tenant_id)
        return jsonify(sanitize_response(tag))
    except:
        return error_response("Tag not found", 404)


@bp.post("/")
def create_tag():
    try:
        tenant_id = get_tenant_id()
        data = TagCreate(**request.json)
        tag = TagService.create(data, tenant_id)
        return jsonify(sanitize_response(tag)), 201
    except Exception as e:
        return error_response(f"Failed to create tag: {str(e)}", 400)


@bp.put("/<id>")
def update_tag(id):
    try:
        tenant_id = get_tenant_id()
        data = TagUpdate(**request.json)
        tag = TagService.update(id, data, tenant_id)
        return jsonify(sanitize_response(tag))
    except Exception as e:
        return error_response(f"Failed to update tag: {str(e)}", 400)


@bp.delete("/<id>")
def delete_tag(id):
    try:
        tenant_id = get_tenant_id()
        return jsonify(TagService.delete(id, tenant_id))
    except:
        return error_response("Tag not found", 404)

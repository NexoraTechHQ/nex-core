# inventory/api/rooms.py
from flask import Blueprint, request, jsonify
from app.core.schemas.room import RoomCreate, RoomUpdate
from app.inventory.services.room_service import RoomService
from app.shared.utils.response import sanitize_response, error_response

bp = Blueprint("rooms", __name__, url_prefix="/api/inventory/rooms")


def get_tenant_id():
    return request.headers.get("X-Tenant-ID")


@bp.get("/")
def list_roles():
    try:
        tenant_id = get_tenant_id()
        rooms = RoomService.list(request.args.to_dict(), tenant_id)
        return jsonify(sanitize_response(rooms))
    except Exception as e:
        return error_response(f"Failed to fetch rooms: {str(e)}", 400)


@bp.get("/<id>")
def get_room(id):
    try:
        tenant_id = get_tenant_id()
        room = RoomService.get(id, tenant_id)
        return jsonify(sanitize_response(room))
    except:
        return error_response("Role not found", 404)


@bp.post("/")
def create_role():
    try:
        tenant_id = get_tenant_id()
        data = RoomCreate(**request.json)
        room = RoomService.create(data, tenant_id)
        return jsonify(sanitize_response(room)), 201
    except Exception as e:
        return error_response(f"Failed to create room: {str(e)}", 400)


@bp.put("/<id>")
def update_room(id):
    try:
        tenant_id = get_tenant_id()
        data = RoomUpdate(**request.json)
        room = RoomService.update(id, data, tenant_id)
        return jsonify(sanitize_response(room))
    except Exception as e:
        return error_response(f"Failed to update room: {str(e)}", 400)


@bp.delete("/<id>")
def delete_room(id):
    try:
        tenant_id = get_tenant_id()
        return jsonify(RoomService.delete(id, tenant_id))
    except:
        return error_response("Role not found", 404)

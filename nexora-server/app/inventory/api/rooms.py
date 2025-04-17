import logging
from flask import Blueprint, request, jsonify
from app.core.schemas.room import RoomCreate, RoomUpdate
from app.inventory.services.room_service import room_service
from app.core.middleware.auth_utils import get_token
from app.shared.exceptions import handle_exceptions

logger = logging.getLogger(__name__)

bp = Blueprint("rooms", __name__, url_prefix="/api/inventory/rooms")

@bp.route("/", methods=["GET"])
@handle_exceptions
@get_token
def list_rooms():
    """List rooms for the authenticated user's tenant with pagination and filtering"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(f"Received query params for listing rooms: {query_params}")
    logger.debug(f"Listing rooms for tenant {tenant_id} with params: {query_params}")
    rooms = room_service.list(query_params, tenant_id)
    return jsonify(rooms)

@bp.route("/<id>", methods=["GET"])
@handle_exceptions
@get_token
def get_room(id):
    """Get a room by ID for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(f"Fetching room {id} for tenant {tenant_id} with params: {query_params}")
    room = room_service.get(id, tenant_id, query_params)
    return jsonify(room)

@bp.route("/", methods=["POST"])
@handle_exceptions
@get_token
def create_room():
    """Create a new room for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    data = RoomCreate(**request.get_json())
    query_params = request.args.to_dict()
    logger.debug(f"Creating room for tenant {tenant_id}: {data} with params: {query_params}")
    room = room_service.create(data, tenant_id, query_params)
    return jsonify(room), 201

@bp.route("/<id>", methods=["PUT"])
@handle_exceptions
@get_token
def update_room(id):
    """Update a room for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    data = RoomUpdate(**request.get_json())
    query_params = request.args.to_dict()
    logger.debug(f"Updating room {id} for tenant {tenant_id}: {data} with params: {query_params}")
    room = room_service.update(id, data, tenant_id, query_params)
    return jsonify(room)

@bp.route("/<id>", methods=["DELETE"])
@handle_exceptions
@get_token
def delete_room(id):
    """Delete a room for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    logger.debug(f"Deleting room {id} for tenant {tenant_id}")
    result = room_service.delete(id, tenant_id)
    return jsonify(result)
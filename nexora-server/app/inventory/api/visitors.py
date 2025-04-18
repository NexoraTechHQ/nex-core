import logging
from flask import Blueprint, request, jsonify
from app.core.schemas.visitor import VisitorCreate, VisitorUpdate
from app.inventory.services.visitor_service import visitor_service
from app.core.middleware.auth_utils import get_token
from app.shared.exceptions import BadRequestException, handle_exceptions

logger = logging.getLogger(__name__)

bp = Blueprint("visitors", __name__, url_prefix="/api/inventory/visitors")


@bp.route("/", methods=["GET"])
@handle_exceptions
@get_token
def list_visitors():
    """List visitors for the authenticated user's tenant with pagination and filtering"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(
        f"Listing visitors for tenant {tenant_id} with params: {query_params}")
    visitors = visitor_service.list(query_params, tenant_id)
    return jsonify(visitors)


@bp.route("/<id>", methods=["GET"])
@handle_exceptions
@get_token
def get_visitor(id):
    """Get a visitor by ID for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    query_params = request.args.to_dict()
    logger.debug(
        f"Fetching visitor {id} for tenant {tenant_id} with params: {query_params}")
    visitor = visitor_service.get(id, tenant_id, query_params)
    return jsonify(visitor)


@bp.route("/", methods=["POST"])
@handle_exceptions
@get_token
def create_visitor():
    """Create a new visitor with image uploads for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    content_type = request.content_type or ""

    # Handle JSON or multipart/form-data
    try:
        if "multipart/form-data" in content_type:
            if not request.form.get("data"):
                raise BadRequestException("Missing 'data' field in form")
            data_json = request.form.get("data")
            data = VisitorCreate.model_validate_json(data_json)
        elif "application/json" in content_type:
            data_dict = request.get_json()
            if not data_dict:
                raise BadRequestException("Invalid or empty JSON body")
            data = VisitorCreate.model_validate(data_dict)
        else:
            raise BadRequestException(
                "Unsupported Content-Type. Use application/json or multipart/form-data")
    except Exception as e:
        logger.error(f"Invalid visitor data: {str(e)}")
        raise BadRequestException(f"Invalid visitor data: {str(e)}")

    query_params = request.args.to_dict()
    logger.debug(
        f"Creating visitor for tenant {tenant_id}: {data} with params: {query_params}")
    visitor = visitor_service.create(data, tenant_id, query_params)
    return jsonify(visitor), 201


@bp.route("/<id>", methods=["PUT"])
@handle_exceptions
@get_token
def update_visitor(id):
    """Update a visitor with image uploads for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    content_type = request.content_type or ""

    # Handle JSON or multipart/form-data
    try:
        if "multipart/form-data" in content_type:
            if not request.form.get("data"):
                raise BadRequestException("Missing 'data' field in form")
            data_json = request.form.get("data")
            data = VisitorUpdate.model_validate_json(data_json)
        elif "application/json" in content_type:
            data_dict = request.get_json()
            if not data_dict:
                raise BadRequestException("Invalid or empty JSON body")
            data = VisitorUpdate.model_validate(data_dict)
        else:
            raise BadRequestException(
                "Unsupported Content-Type. Use application/json or multipart/form-data")
    except Exception as e:
        logger.error(f"Invalid visitor data: {str(e)}")
        raise BadRequestException(f"Invalid visitor data: {str(e)}")

    query_params = request.args.to_dict()
    logger.debug(
        f"Updating visitor {id} for tenant {tenant_id}: {data} with params: {query_params}")
    visitor = visitor_service.update(id, data, tenant_id, query_params)
    return jsonify(visitor)


@bp.route("/<id>", methods=["DELETE"])
@handle_exceptions
@get_token
def delete_visitor(id):
    """Delete a visitor for the authenticated user's tenant"""
    tenant_id = request.tenant_id
    logger.debug(f"Deleting visitor {id} for tenant {tenant_id}")
    result = visitor_service.delete(id, tenant_id)
    return jsonify(result)

from flask import Blueprint, request, jsonify
from app.core.schemas.department import DepartmentCreate, DepartmentUpdate
from app.inventory.services.department_service import DepartmentService

bp = Blueprint("departments", __name__,
               url_prefix="/api/inventory/departments")


@bp.get("/")
def list_departments():
    return jsonify([d.__dict__ for d in DepartmentService.list()])


@bp.get("/<id>")
def get_department(id):
    return jsonify(DepartmentService.get(id).__dict__)


@bp.post("/")
def create_department():
    data = DepartmentCreate(**request.json)
    return jsonify(DepartmentService.create(data).__dict__)


@bp.put("/<id>")
def update_department(id):
    data = DepartmentUpdate(**request.json)
    return jsonify(DepartmentService.update(id, data).__dict__)


@bp.delete("/<id>")
def delete_department(id):
    return jsonify(DepartmentService.delete(id))

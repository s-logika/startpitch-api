from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

startups_bp = Blueprint("startups", __name__, url_prefix="/api/v1/startups")
STARTUPS: dict[int, dict] = {}


@startups_bp.post("")
@jwt_required()
def create_startup():
    data = request.get_json() or {}
    startup_id = len(STARTUPS) + 1
    data["id"] = startup_id
    STARTUPS[startup_id] = data
    return jsonify(data), 201


@startups_bp.get("/<int:startup_id>")
@jwt_required()
def get_startup(startup_id: int):
    startup = STARTUPS.get(startup_id)
    if not startup:
        return jsonify({"error": "Startup not found"}), 404
    return jsonify(startup), 200


@startups_bp.patch("/<int:startup_id>")
@jwt_required()
def update_startup(startup_id: int):
    startup = STARTUPS.get(startup_id)
    if not startup:
        return jsonify({"error": "Startup not found"}), 404
    data = request.get_json() or {}
    startup.update(data)
    return jsonify(startup), 200

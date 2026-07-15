from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.startup import Startup

startups_bp = Blueprint("startups", __name__, url_prefix="/api/v1/startups")


@startups_bp.post("")
@jwt_required()
def create_startup():
    data = request.get_json(silent=True) or {}
    startup = Startup(data=data)
    db.session.add(startup)
    db.session.commit()
    return jsonify(startup.to_dict()), 201


@startups_bp.get("/<int:startup_id>")
@jwt_required()
def get_startup(startup_id: int):
    startup = db.session.get(Startup, startup_id)
    if not startup:
        return jsonify({"error": "Startup not found"}), 404
    return jsonify(startup.to_dict()), 200


@startups_bp.patch("/<int:startup_id>")
@jwt_required()
def update_startup(startup_id: int):
    startup = db.session.get(Startup, startup_id)
    if not startup:
        return jsonify({"error": "Startup not found"}), 404
    data = request.get_json(silent=True) or {}
    startup.data = {**(startup.data or {}), **data}
    db.session.commit()
    return jsonify(startup.to_dict()), 200

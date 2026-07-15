from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.mentor import Mentor

mentors_bp = Blueprint("mentors", __name__, url_prefix="/api/v1/mentors")


@mentors_bp.get("")
@jwt_required()
def list_mentors():
    expertise = request.args.get("expertise")
    availability = request.args.get("availability")
    results = [m.to_dict() for m in Mentor.query.all()]
    if expertise:
        results = [m for m in results if expertise in m.get("expertise", [])]
    if availability:
        results = [m for m in results if m.get("availability") == availability]
    return jsonify(results), 200


@mentors_bp.get("/<int:mentor_id>")
@jwt_required()
def get_mentor(mentor_id: int):
    mentor = db.session.get(Mentor, mentor_id)
    if not mentor:
        return jsonify({"error": "Mentor not found"}), 404
    return jsonify(mentor.to_dict()), 200

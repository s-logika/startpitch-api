from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

reputation_bp = Blueprint("reputation", __name__, url_prefix="/api/v1/reputation")
REPUTATION: dict[int, dict] = {}


@reputation_bp.get("/<int:user_id>")
@jwt_required()
def get_reputation(user_id: int):
    item = REPUTATION.get(user_id, {"user_id": user_id, "score": 0, "ratings": []})
    return jsonify(item), 200


@reputation_bp.post("/<int:user_id>/rate")
@jwt_required()
def rate_user(user_id: int):
    data = request.get_json(silent=True) or {}
    item = REPUTATION.setdefault(user_id, {"user_id": user_id, "score": 0, "ratings": []})
    item["ratings"].append(data.get("rating", 0))
    if item["ratings"]:
        item["score"] = round(sum(item["ratings"]) / len(item["ratings"]), 2)
    return jsonify(item), 201


@reputation_bp.get("/<int:user_id>/badges")
@jwt_required()
def get_badges(user_id: int):
    score = REPUTATION.get(user_id, {}).get("score", 0)
    badges = ["trusted"] if score >= 4 else ["new"]
    return jsonify({"user_id": user_id, "badges": badges}), 200

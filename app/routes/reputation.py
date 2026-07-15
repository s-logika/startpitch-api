from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.reputation import Reputation

reputation_bp = Blueprint("reputation", __name__, url_prefix="/api/v1/reputation")


@reputation_bp.get("/<int:user_id>")
@jwt_required()
def get_reputation(user_id: int):
    item = db.session.get(Reputation, user_id)
    if not item:
        return jsonify({"user_id": user_id, "score": 0, "ratings": []}), 200
    return jsonify(item.to_dict()), 200


@reputation_bp.post("/<int:user_id>/rate")
@jwt_required()
def rate_user(user_id: int):
    data = request.get_json(silent=True) or {}
    item = db.session.get(Reputation, user_id)
    if not item:
        item = Reputation(user_id=user_id, score=0, ratings=[])
        db.session.add(item)
    ratings = list(item.ratings or [])
    ratings.append(data.get("rating", 0))
    item.ratings = ratings
    if ratings:
        item.score = round(sum(ratings) / len(ratings), 2)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@reputation_bp.get("/<int:user_id>/badges")
@jwt_required()
def get_badges(user_id: int):
    item = db.session.get(Reputation, user_id)
    score = item.score if item else 0
    badges = ["trusted"] if score >= 4 else ["new"]
    return jsonify({"user_id": user_id, "badges": badges}), 200

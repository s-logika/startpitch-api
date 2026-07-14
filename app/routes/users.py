from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services.auth_service import USERS

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_bp.get("/me")
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = next((u for u in USERS.values() if str(u["id"]) == str(user_id)), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user["id"], "email": user["email"], "role": user["role"]}), 200


@users_bp.patch("/me")
@jwt_required()
def patch_me():
    claims = get_jwt()
    user = USERS.get(claims["email"])
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json() or {}
    user["profile"] = {**user.get("profile", {}), **data}
    return jsonify({"updated": True, "profile": user["profile"]}), 200


@users_bp.get("/<int:user_id>/profile-completeness")
@jwt_required()
def profile_completeness(user_id: int):
    user = next((u for u in USERS.values() if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    profile = user.get("profile", {})
    fields = ["name", "bio", "role"]
    filled = sum(1 for field in fields if profile.get(field) or user.get(field))
    score = int((filled / len(fields)) * 100)
    return jsonify({"user_id": user_id, "score": score}), 200

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

deal_rooms_bp = Blueprint("deal_rooms", __name__, url_prefix="/api/v1/deal-rooms")
DEAL_ROOMS: dict[int, dict] = {}


@deal_rooms_bp.post("")
@jwt_required()
def create_deal_room():
    data = request.get_json() or {}
    room_id = len(DEAL_ROOMS) + 1
    data["id"] = room_id
    data["documents"] = []
    data["access_logs"] = []
    DEAL_ROOMS[room_id] = data
    return jsonify(data), 201


@deal_rooms_bp.get("/<int:room_id>")
@jwt_required()
def get_deal_room(room_id: int):
    room = DEAL_ROOMS.get(room_id)
    if not room:
        return jsonify({"error": "Deal room not found"}), 404
    return jsonify(room), 200


@deal_rooms_bp.post("/<int:room_id>/nda/sign")
@jwt_required()
def sign_nda(room_id: int):
    room = DEAL_ROOMS.get(room_id)
    if not room:
        return jsonify({"error": "Deal room not found"}), 404
    room["nda_signed"] = True
    return jsonify({"room_id": room_id, "nda_signed": True}), 200


@deal_rooms_bp.post("/<int:room_id>/documents")
@jwt_required()
def add_document(room_id: int):
    room = DEAL_ROOMS.get(room_id)
    if not room:
        return jsonify({"error": "Deal room not found"}), 404
    data = request.get_json() or {}
    doc = {"id": len(room["documents"]) + 1, "name": data.get("name"), "url": data.get("url")}
    room["documents"].append(doc)
    return jsonify(doc), 201


@deal_rooms_bp.get("/<int:room_id>/documents/<int:doc_id>/download")
@jwt_required()
def download_document(room_id: int, doc_id: int):
    room = DEAL_ROOMS.get(room_id)
    if not room:
        return jsonify({"error": "Deal room not found"}), 404
    doc = next((d for d in room["documents"] if d["id"] == doc_id), None)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    room["access_logs"].append({"event": "download", "doc_id": doc_id})
    return jsonify({"download_url": doc["url"]}), 200


@deal_rooms_bp.get("/<int:room_id>/access-logs")
@jwt_required()
def access_logs(room_id: int):
    room = DEAL_ROOMS.get(room_id)
    if not room:
        return jsonify({"error": "Deal room not found"}), 404
    return jsonify(room["access_logs"]), 200

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

messages_bp = Blueprint("messages", __name__, url_prefix="/api/v1/messages")
MESSAGES: list[dict] = []


@messages_bp.post("")
@jwt_required()
def create_message():
    data = request.get_json() or {}
    data["id"] = len(MESSAGES) + 1
    MESSAGES.append(data)
    return jsonify(data), 201


@messages_bp.get("")
@jwt_required()
def list_messages():
    thread_with = request.args.get("thread_with")
    deal_room_id = request.args.get("deal_room_id")
    results = MESSAGES
    if thread_with:
        results = [m for m in results if str(m.get("to")) == thread_with or str(m.get("from")) == thread_with]
    if deal_room_id:
        results = [m for m in results if str(m.get("deal_room_id")) == deal_room_id]
    return jsonify(results), 200

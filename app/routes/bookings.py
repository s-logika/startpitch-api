from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/v1/bookings")
BOOKINGS: dict[int, dict] = {}


@bookings_bp.post("")
@jwt_required()
def create_booking():
    data = request.get_json(silent=True) or {}
    booking_id = len(BOOKINGS) + 1
    data["id"] = booking_id
    BOOKINGS[booking_id] = data
    return jsonify(data), 201


@bookings_bp.get("")
@jwt_required()
def list_bookings():
    user_id = request.args.get("user_id")
    role = request.args.get("role")
    results = list(BOOKINGS.values())
    if user_id:
        results = [b for b in results if str(b.get("user_id")) == user_id]
    if role:
        results = [b for b in results if b.get("role") == role]
    return jsonify(results), 200


@bookings_bp.patch("/<int:booking_id>")
@jwt_required()
def update_booking(booking_id: int):
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    booking.update(request.get_json(silent=True) or {})
    return jsonify(booking), 200


@bookings_bp.post("/<int:booking_id>/feedback")
@jwt_required()
def booking_feedback(booking_id: int):
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    booking["feedback"] = request.get_json(silent=True) or {}
    return jsonify({"updated": True, "booking": booking}), 201

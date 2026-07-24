from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.booking import Booking
from app.services.notification_service import send_notification

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/v1/bookings")


@bookings_bp.post("")
@jwt_required()
def create_booking():
    data = request.get_json(silent=True) or {}
    booking = Booking(data=data)
    db.session.add(booking)
    db.session.commit()
    user_id = data.get("user_id")
    if user_id:
        send_notification(int(user_id), f"Booking #{booking.id} requested.")
    return jsonify(booking.to_dict()), 201


@bookings_bp.get("")
@jwt_required()
def list_bookings():
    user_id = request.args.get("user_id")
    role = request.args.get("role")
    results = [b.to_dict() for b in Booking.query.all()]
    if user_id:
        results = [b for b in results if str(b.get("user_id")) == user_id]
    if role:
        results = [b for b in results if b.get("role") == role]
    return jsonify(results), 200


@bookings_bp.patch("/<int:booking_id>")
@jwt_required()
def update_booking(booking_id: int):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    updates = request.get_json(silent=True) or {}
    booking.data = {**(booking.data or {}), **updates}
    db.session.commit()
    user_id = booking.data.get("user_id")
    if user_id and "status" in updates:
        send_notification(int(user_id), f"Booking #{booking.id} status changed to {updates['status']}.")
    return jsonify(booking.to_dict()), 200


@bookings_bp.post("/<int:booking_id>/feedback")
@jwt_required()
def booking_feedback(booking_id: int):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    booking.data = {**(booking.data or {}), "feedback": request.get_json(silent=True) or {}}
    db.session.commit()
    return jsonify({"updated": True, "booking": booking.to_dict()}), 201

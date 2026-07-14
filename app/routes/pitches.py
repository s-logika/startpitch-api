from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.file_service import normalize_pitch_payload

pitches_bp = Blueprint("pitches", __name__, url_prefix="/api/v1/pitches")
PITCHES: dict[int, dict] = {}
PITCH_VERSIONS: dict[int, list[dict]] = {}


@pitches_bp.post("")
@jwt_required()
def create_pitch():
    data = normalize_pitch_payload(request.get_json() or {})
    pitch_id = len(PITCHES) + 1
    data["id"] = pitch_id
    data["startup_id"] = (request.get_json() or {}).get("startup_id")
    PITCHES[pitch_id] = data
    return jsonify(data), 201


@pitches_bp.get("/<int:pitch_id>")
@jwt_required()
def get_pitch(pitch_id: int):
    pitch = PITCHES.get(pitch_id)
    if not pitch:
        return jsonify({"error": "Pitch not found"}), 404
    return jsonify(pitch), 200


@pitches_bp.get("")
@jwt_required()
def list_pitches():
    startup_id = request.args.get("startup_id")
    visibility = request.args.get("visibility")
    results = list(PITCHES.values())
    if startup_id:
        results = [p for p in results if str(p.get("startup_id")) == startup_id]
    if visibility:
        results = [p for p in results if p.get("visibility") == visibility]
    return jsonify(results), 200


@pitches_bp.post("/<int:pitch_id>/versions")
@jwt_required()
def add_version(pitch_id: int):
    if pitch_id not in PITCHES:
        return jsonify({"error": "Pitch not found"}), 404
    payload = request.get_json() or {}
    version = {
        "id": len(PITCH_VERSIONS.get(pitch_id, [])) + 1,
        "pitch_id": pitch_id,
        "content_url": payload.get("content_url"),
        "status": "queued",
    }
    PITCH_VERSIONS.setdefault(pitch_id, []).append(version)
    return jsonify(version), 201


@pitches_bp.get("/<int:pitch_id>/versions")
@jwt_required()
def list_versions(pitch_id: int):
    return jsonify(PITCH_VERSIONS.get(pitch_id, [])), 200


@pitches_bp.get("/<int:pitch_id>/versions/<int:version_id>")
@jwt_required()
def get_version(pitch_id: int, version_id: int):
    version = next((v for v in PITCH_VERSIONS.get(pitch_id, []) if v["id"] == version_id), None)
    if not version:
        return jsonify({"error": "Version not found"}), 404
    return jsonify(version), 200


@pitches_bp.get("/<int:pitch_id>/versions/<int:version_id>/status")
@jwt_required()
def get_version_status(pitch_id: int, version_id: int):
    version = next((v for v in PITCH_VERSIONS.get(pitch_id, []) if v["id"] == version_id), None)
    if not version:
        return jsonify({"error": "Version not found"}), 404
    return jsonify({"status": version.get("status", "queued")}), 200


@pitches_bp.get("/<int:pitch_id>/score-history")
@jwt_required()
def score_history(pitch_id: int):
    history = [
        {"version_id": v["id"], "overall_score": 70 + v["id"], "delta": 1}
        for v in PITCH_VERSIONS.get(pitch_id, [])
    ]
    return jsonify(history), 200

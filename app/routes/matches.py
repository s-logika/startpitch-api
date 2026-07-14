from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.routes.startups import STARTUPS
from app.services.matching_service import compute_match_score

matches_bp = Blueprint("matches", __name__, url_prefix="/api/v1")
THESES: dict[int, dict] = {}
MATCHES: dict[int, dict] = {}


@matches_bp.post("/thesis")
@jwt_required()
def upsert_thesis():
    data = request.get_json(silent=True) or {}
    try:
        investor_id = int(data.get("investor_id", len(THESES) + 1))
    except (TypeError, ValueError):
        return jsonify({"error": "investor_id must be an integer"}), 400
    data["investor_id"] = investor_id
    THESES[investor_id] = data
    return jsonify(data), 201


@matches_bp.get("/thesis/<int:investor_id>")
@jwt_required()
def get_thesis(investor_id: int):
    thesis = THESES.get(investor_id)
    if not thesis:
        return jsonify({"error": "Thesis not found"}), 404
    return jsonify(thesis), 200


@matches_bp.get("/matches/for-investor/<int:investor_id>")
@jwt_required()
def matches_for_investor(investor_id: int):
    results = [m for m in MATCHES.values() if m["investor_id"] == investor_id]
    return jsonify(results), 200


@matches_bp.get("/matches/for-startup/<int:startup_id>")
@jwt_required()
def matches_for_startup(startup_id: int):
    results = [m for m in MATCHES.values() if m["startup_id"] == startup_id]
    return jsonify(results), 200


@matches_bp.get("/matches/<int:match_id>/rationale")
@jwt_required()
def get_rationale(match_id: int):
    match = MATCHES.get(match_id)
    if not match:
        return jsonify({"error": "Match not found"}), 404
    return jsonify(match.get("rationale", {})), 200


@matches_bp.post("/matches/recompute")
@jwt_required()
def recompute_matches():
    MATCHES.clear()
    for investor_id, thesis in THESES.items():
        for startup_id, startup in STARTUPS.items():
            computed = compute_match_score(startup, thesis)
            match_id = len(MATCHES) + 1
            MATCHES[match_id] = {
                "id": match_id,
                "investor_id": investor_id,
                "startup_id": startup_id,
                **computed,
            }
    return jsonify(list(MATCHES.values())), 200

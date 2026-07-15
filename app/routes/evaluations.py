from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.evaluation import EvaluationJob
from app.services.ai_service import queue_evaluation

evaluations_bp = Blueprint("evaluations", __name__, url_prefix="/api/v1/evaluations")


@evaluations_bp.post("")
@jwt_required()
def create_evaluation():
    data = request.get_json(silent=True) or {}
    job = queue_evaluation(data.get("pitch_version_id", 0))
    return jsonify(job), 202


@evaluations_bp.get("/jobs/<int:job_id>")
@jwt_required()
def get_job(job_id: int):
    job = db.session.get(EvaluationJob, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.to_dict()), 200


@evaluations_bp.get("/<int:pitch_version_id>")
@jwt_required()
def get_evaluation(pitch_version_id: int):
    job = EvaluationJob.query.filter_by(pitch_version_id=pitch_version_id, status="done").first()
    if not job:
        return jsonify({"error": "Evaluation not ready"}), 404
    return jsonify(job.to_dict()), 200


@evaluations_bp.post("/<int:evaluation_id>/override")
@jwt_required()
def override_evaluation(evaluation_id: int):
    job = db.session.get(EvaluationJob, evaluation_id)
    if not job:
        return jsonify({"error": "Evaluation not found"}), 404
    data = request.get_json(silent=True) or {}
    job.data = {**(job.data or {}), "override": data}
    db.session.commit()
    return jsonify({"updated": True, "evaluation": job.to_dict()}), 200

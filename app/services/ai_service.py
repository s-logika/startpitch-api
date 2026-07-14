from concurrent.futures import ThreadPoolExecutor
from time import sleep

executor = ThreadPoolExecutor(max_workers=2)
EVALUATION_JOBS: dict[int, dict] = {}


def _run_evaluation(job_id: int, pitch_version_id: int) -> None:
    sleep(2)
    EVALUATION_JOBS[job_id] = {
        "id": job_id,
        "pitch_version_id": pitch_version_id,
        "status": "done",
        "score": {
            "market": 78,
            "team": 82,
            "traction": 70,
            "financials": 73,
            "defensibility": 76,
            "clarity": 80,
            "overall": 76.5,
        },
        "feedback": {
            "market": [
                {
                    "claim": "Large target segment",
                    "evidence_snippet_from_pitch": "Addressing mid-sized SaaS firms",
                    "verdict": "reasonable",
                }
            ]
        },
    }


def queue_evaluation(pitch_version_id: int) -> dict:
    job_id = len(EVALUATION_JOBS) + 1
    EVALUATION_JOBS[job_id] = {
        "id": job_id,
        "pitch_version_id": pitch_version_id,
        "status": "processing",
    }
    executor.submit(_run_evaluation, job_id, pitch_version_id)
    return EVALUATION_JOBS[job_id]

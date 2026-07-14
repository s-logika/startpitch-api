from dataclasses import dataclass


@dataclass
class Evaluation:
    id: int
    pitch_version_id: int
    status: str

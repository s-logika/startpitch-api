from dataclasses import dataclass


@dataclass
class Pitch:
    id: int
    startup_id: int
    title: str
    visibility: str = "private"

from dataclasses import dataclass


@dataclass
class DealRoom:
    id: int
    startup_id: int
    nda_required: bool

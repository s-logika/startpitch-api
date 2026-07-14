from dataclasses import dataclass


@dataclass
class Notification:
    id: int
    user_id: int
    message: str
    read: bool = False

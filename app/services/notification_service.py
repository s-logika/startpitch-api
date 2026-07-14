NOTIFICATIONS: list[dict] = []


def send_notification(user_id: int, message: str) -> dict:
    item = {
        "id": len(NOTIFICATIONS) + 1,
        "user_id": user_id,
        "message": message,
        "read": False,
    }
    NOTIFICATIONS.append(item)
    return item

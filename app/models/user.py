from datetime import datetime, timezone

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="founder")
    profile = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self, include_profile: bool = True) -> dict:
        data = {"id": self.id, "email": self.email, "role": self.role}
        if include_profile:
            data["profile"] = self.profile or {}
        return data

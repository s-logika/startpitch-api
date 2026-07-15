from app.extensions import db


class Pitch(db.Model):
    __tablename__ = "pitches"

    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=True, index=True)
    visibility = db.Column(db.String(50), nullable=False, default="private")
    data = db.Column(db.JSON, nullable=False, default=dict)

    def to_dict(self) -> dict:
        return {**(self.data or {}), "id": self.id, "startup_id": self.startup_id, "visibility": self.visibility}


class PitchVersion(db.Model):
    __tablename__ = "pitch_versions"

    id = db.Column(db.Integer, primary_key=True)
    local_id = db.Column(db.Integer, nullable=False)
    pitch_id = db.Column(db.Integer, db.ForeignKey("pitches.id"), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default="queued")
    data = db.Column(db.JSON, nullable=False, default=dict)

    def to_dict(self) -> dict:
        return {**(self.data or {}), "id": self.local_id, "pitch_id": self.pitch_id, "status": self.status}

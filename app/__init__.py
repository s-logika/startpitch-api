from flask import Flask, jsonify

from app.config import Config
from app.extensions import bcrypt, cors, jwt
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.bookings import bookings_bp
from app.routes.deal_rooms import deal_rooms_bp
from app.routes.evaluations import evaluations_bp
from app.routes.matches import matches_bp
from app.routes.mentors import mentors_bp
from app.routes.messages import messages_bp
from app.routes.notifications import notifications_bp
from app.routes.pitches import pitches_bp
from app.routes.reputation import reputation_bp
from app.routes.startups import startups_bp
from app.routes.users import users_bp
from app.routes.voice import voice_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    blueprints = [
        auth_bp,
        users_bp,
        startups_bp,
        pitches_bp,
        evaluations_bp,
        matches_bp,
        reputation_bp,
        mentors_bp,
        bookings_bp,
        deal_rooms_bp,
        messages_bp,
        notifications_bp,
        voice_bp,
        admin_bp,
    ]
    for bp in blueprints:
        app.register_blueprint(bp)

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    return app

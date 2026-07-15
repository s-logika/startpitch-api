import os
import urllib.parse

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", str(60 * int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "30"))))
    )
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800"))

    JSON_SORT_KEYS = False

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "startpitch_db")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"mysql+pymysql://{urllib.parse.quote_plus(DB_USER)}:{urllib.parse.quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

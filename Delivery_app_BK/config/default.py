import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY","devkey")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"options": "-c timezone=UTC"}
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

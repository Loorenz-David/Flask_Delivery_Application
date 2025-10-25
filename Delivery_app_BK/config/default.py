import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY","devkey")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    SQLALCHEMY_TRACK_MODIFICATIONS = False

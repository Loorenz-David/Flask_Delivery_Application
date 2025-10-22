import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY","devkey")
    QLALCHEMY_TRACK_MODIFICATIONS = False
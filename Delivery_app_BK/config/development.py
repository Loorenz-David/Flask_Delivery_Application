from Delivery_app_BK.config.default import Config
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL","postgresql://postgres:0698@localhost:5432/DeliveryApp")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or Config.SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

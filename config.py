
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Automatically create database directory
DATABASE_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DATABASE_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "ai-finance-assistant-development-key"
    )

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(DATABASE_DIR, "finance.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

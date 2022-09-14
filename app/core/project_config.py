import os, uuid
import logging
from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_pc_unique_id():
    return str(hex(uuid.getnode()))


def get_ip(url: str):
    return url.split(':')[0]


# A class that contains all the settings for the project.
class Settings(BaseSettings):
    PROJECT_NAME = os.getenv("PROJECT_NAME", "ULTIMATE STORE MANAGEMENT")
    SECRET_KEY = os.getenv("SECRET_KEY", "20194060")
    API_PREFIX = ""
    BACKEND_CORS_ORIGINS = ["*"]
    BACKEND_PORT = os.getenv("BACKEND_PORT", 4060)
    FRONTEND_PORT = os.getenv("FRONTEND_PORT", 4953)
    ELASTIC_URL = os.getenv("ELASTIC_URL", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # Token expired after 7 days
    SECURITY_ALGORITHM = "HS256"
    LOG_LEVEL = logging.DEBUG
    LOG_DIR_MAPPING = BASE_DIR + r'/resources/log_dir_config.yaml'
    RESPONSE_CODE_DIR = BASE_DIR + r'/resources/response_code.json'
    LOG_DIR = os.getenv("LOG_DIR", BASE_DIR)
    LOG_TIME_OUT = os.getenv("LOG_TIME_OUT", 5)
    REDIS_MAXMEMORY = os.getenv("REDIS_MAXMEMORY", "50M")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_POLICY = os.getenv("REDIS_POLICY", "allkeys-lru")
    REDIS_TIME_TO_LIVE = os.getenv("REDIS_TIME_TO_LIVE", 60 * 60 * 24)
    BACKEND_NAME = os.path.basename(BASE_DIR)
    IMAGE_WIDTH = os.getenv("IMAGE_WIDTH", 400)
    IMAGE_HEIGHT = os.getenv("IMAGE_HEIGHT", 500)
    AI_DIR = os.getenv("AI_DIR", str(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../usm-model/"))))
    UI_DIR = os.getenv("UI_DIR", BASE_DIR + r'/build')

settings = Settings()
print(settings)

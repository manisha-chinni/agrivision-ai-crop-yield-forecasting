from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

@lru_cache
def get_settings():
    return {
        "provider": os.getenv("DATA_PROVIDER", "demo").lower(),
        "gee_project": os.getenv("GOOGLE_EARTH_ENGINE_PROJECT", ""),
        "model_path": os.getenv("MODEL_PATH", ""),
        "cors_origins": [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip()],
    }

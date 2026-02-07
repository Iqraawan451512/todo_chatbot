import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from the backend directory regardless of cwd
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env", override=True)


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")


settings = Settings()

# Ensure the OpenAI Agents SDK can find the API key
if settings.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

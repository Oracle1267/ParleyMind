import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(env_path)

DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parents[1] / "instance" / "parlaymind.db"))
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "parleymind-scraper")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

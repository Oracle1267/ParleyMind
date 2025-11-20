import os
from dotenv import load_dotenv

load_dotenv()

def require_env(varname):
    val = os.getenv(varname)
    if not val:
        raise RuntimeError(f"Missing required env variable: {varname}")
    return val

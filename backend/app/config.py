"""Settings read from environment variables, so the same code runs on your laptop and on a server."""
import os

DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"


def allowed_origins() -> list[str]:
    """Websites allowed to call this API. Set ALLOWED_ORIGINS="https://your-app.vercel.app" on the server.
    Several addresses can be given, separated by commas."""
    raw = os.environ.get("ALLOWED_ORIGINS", DEFAULT_ORIGINS)
    return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]

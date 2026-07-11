"""Application configuration, loaded from environment variables."""
from __future__ import annotations

import os
from functools import lru_cache


class Settings:
    """Simple env-driven settings (kept dependency-light; no BaseSettings
    requirement so this loads even before pydantic-settings is installed)."""

    APP_NAME: str = "OrbitOps India"
    APP_VERSION: str = "1.0.0"

    # CORS: comma-separated list of allowed origins
    CORS_ORIGINS: list[str] = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")

    # TLE data source
    CELESTRAK_BASE_URL: str = os.environ.get(
        "CELESTRAK_BASE_URL", "https://celestrak.org/NORAD/elements/gp.php"
    )
    TLE_CACHE_TTL_SECONDS: int = int(os.environ.get("TLE_CACHE_TTL_SECONDS", str(6 * 3600)))
    TLE_FETCH_TIMEOUT_SECONDS: float = float(os.environ.get("TLE_FETCH_TIMEOUT_SECONDS", "6.0"))

    # Force demo/archive mode even if network is available (useful for
    # reliable classroom demos / offline grading)
    FORCE_DEMO_MODE: bool = os.environ.get("FORCE_DEMO_MODE", "false").lower() == "true"

    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()

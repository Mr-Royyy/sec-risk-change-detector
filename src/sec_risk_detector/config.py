"""Project configuration helpers.

Configuration is intentionally centralized so the rest of the codebase does not
need to repeatedly read environment variables or hard-code paths.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class ProjectConfig:
    """Runtime settings for the project.

    Attributes:
        sec_user_agent: User-Agent header used for SEC requests. SEC fair-access
            guidance expects automated tools to identify themselves.
        cache_dir: Local cache directory for API and filing responses.
        request_timeout: HTTP timeout in seconds.
        max_requests_per_second: Conservative request limit for SEC endpoints.
    """

    sec_user_agent: str
    cache_dir: Path
    request_timeout: int = 30
    max_requests_per_second: float = 5.0

    @classmethod
    def from_env(cls) -> "ProjectConfig":
        """Create config from environment variables and .env if present."""

        load_dotenv()
        user_agent = os.getenv("SEC_USER_AGENT", "SecRiskDetector student@example.com")
        cache_dir = Path(os.getenv("CACHE_DIR", "data/raw/cache"))
        return cls(sec_user_agent=user_agent, cache_dir=cache_dir)

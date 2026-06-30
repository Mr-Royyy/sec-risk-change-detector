"""Simple rate limiter for polite SEC access."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    """Block briefly before requests to avoid exceeding a target rate.

    This limiter is intentionally conservative and simple. It is enough for the
    project MVP where requests happen sequentially.
    """

    max_requests_per_second: float
    _last_request_time: float = field(default=0.0, init=False)

    def wait(self) -> None:
        """Sleep until it is safe to make the next request."""

        if self.max_requests_per_second <= 0:
            return

        min_interval = 1.0 / self.max_requests_per_second
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request_time = time.monotonic()

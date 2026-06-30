"""Small disk cache for SEC API responses.

A cache is important because SEC data endpoints should be accessed efficiently.
This class stores raw response text on disk using a hashed cache key.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DiskCache:
    """File-based cache for JSON and text responses.

    Attributes:
        root_dir: Directory where cached files are stored.
    """

    root_dir: Path

    def __post_init__(self) -> None:
        """Create the cache directory if it does not already exist."""

        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _path_for_key(self, key: str, suffix: str) -> Path:
        """Build a safe filesystem path for a cache key.

        Args:
            key: Stable cache key, often a URL.
            suffix: File extension including the dot, such as `.json`.

        Returns:
            A cache file path under `root_dir`.
        """

        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.root_dir / f"{digest}{suffix}"

    def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        """Read cached JSON for a key.

        Returns None when the cache entry does not exist.
        """

        path = self._path_for_key(key, ".json")
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set_json(self, key: str, value: dict[str, Any] | list[Any]) -> None:
        """Write a JSON-serializable value to the cache."""

        path = self._path_for_key(key, ".json")
        path.write_text(json.dumps(value, indent=2), encoding="utf-8")

    def get_text(self, key: str) -> str | None:
        """Read cached text for a key.

        Returns None when the cache entry does not exist.
        """

        path = self._path_for_key(key, ".txt")
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8", errors="ignore")

    def set_text(self, key: str, value: str) -> None:
        """Write text to the cache."""

        path = self._path_for_key(key, ".txt")
        path.write_text(value, encoding="utf-8", errors="ignore")

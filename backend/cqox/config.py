"""
Minimal settings object for Emotion CQOx.

We avoid external dependencies so tests can run without installing extras.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./emotion.db")
    redis_url: str | None = os.getenv("REDIS_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()

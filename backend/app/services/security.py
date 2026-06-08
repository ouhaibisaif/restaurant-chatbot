from __future__ import annotations

import html
import re
import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?(system|developer)\s+prompt",
    r"show\s+me\s+(your\s+)?(hidden\s+)?instructions",
    r"execute\s+(a\s+)?command",
    r"read\s+(a\s+)?file",
    r"access\s+(the\s+)?filesystem",
]


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, Deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.time()
        bucket = self.requests[key]
        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
        bucket.append(now)


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "local"


def sanitize_text(value: str) -> str:
    cleaned = html.escape(value.strip(), quote=False)
    return re.sub(r"\s+", " ", cleaned)


def looks_like_prompt_injection(value: str) -> bool:
    lower = value.lower()
    return any(re.search(pattern, lower) for pattern in INJECTION_PATTERNS)

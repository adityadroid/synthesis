"""Content moderation service for filtering inappropriate content."""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional

from .logging import get_logger

logger = get_logger(__name__)


class FilterLevel(str, Enum):
    """Content filter levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ModerationResult:
    """Result of content moderation."""

    is_appropriate: bool
    flagged_categories: list[str]
    confidence: float
    message: str | None = None


class ContentModerator:
    """Service for moderating user content."""

    # Basic patterns for content filtering
    PROFANITY_PATTERNS = [
        # Common profanity (minimal set)
        r"\b(badword1|badword2)\b",  # Placeholder - add real patterns
    ]

    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r"<script[^>]*>",  # Script tags
        r"javascript:",  # JavaScript protocol
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>",  # Iframes
        r"data:text/html",  # Data URLs
    ]

    def __init__(self, level: FilterLevel = FilterLevel.MEDIUM):
        self.level = level
        self._profanity_regex = re.compile(
            "|".join(self.PROFANITY_PATTERNS),
            re.IGNORECASE,
        )
        self._suspicious_regex = re.compile(
            "|".join(self.SUSPICIOUS_PATTERNS),
            re.IGNORECASE,
        )

    def moderate(self, content: str) -> ModerationResult:
        """Check content for inappropriate material."""
        if self.level == FilterLevel.NONE:
            return ModerationResult(
                is_appropriate=True,
                flagged_categories=[],
                confidence=1.0,
            )

        flagged = []

        # Check for suspicious patterns (XSS attempts)
        if self._suspicious_regex.search(content):
            flagged.append("suspicious_content")
            logger.warning("Suspicious content pattern detected")

        # Check profanity (only for MEDIUM and HIGH)
        if self.level in [FilterLevel.MEDIUM, FilterLevel.HIGH]:
            if self._profanity_regex.search(content):
                flagged.append("profanity")

        # Check content length
        if len(content) > 50000:
            flagged.append("content_too_long")

        is_appropriate = len(flagged) == 0

        if flagged and self.level == FilterLevel.HIGH:
            message = f"Content flagged for: {', '.join(flagged)}"
        elif flagged:
            message = None  # Don't block, just warn
        else:
            message = None

        return ModerationResult(
            is_appropriate=is_appropriate,
            flagged_categories=flagged,
            confidence=1.0 if is_appropriate else 0.9,
            message=message,
        )

    def sanitize(self, content: str) -> str:
        """Sanitize content by removing potentially dangerous parts."""
        # Remove script-related content
        content = self._suspicious_regex.sub("", content)

        # Remove extra whitespace
        content = re.sub(r"\s+", " ", content)

        return content.strip()


# Global moderator instance
content_moderator = ContentModerator()


def moderate_content(content: str) -> ModerationResult:
    """Quick function to moderate content."""
    return content_moderator.moderate(content)


def sanitize_content(content: str) -> str:
    """Quick function to sanitize content."""
    return content_moderator.sanitize(content)

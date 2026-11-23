import re
import math
from typing import List, Dict, Any


class DocumentMetrics:
    """Calculates live document statistics & outline."""

    @staticmethod
    def compute_stats(text: str) -> Dict[str, Any]:
        clean_text = text.strip()
        if not clean_text:
            return {
                "words": 0,
                "chars": 0,
                "chars_no_spaces": 0,
                "lines": 0,
                "reading_time_mins": 0,
            }

        words = re.findall(r"\b\S+\b", clean_text)
        chars = len(text)
        chars_no_spaces = len(re.sub(r"\s+", "", text))
        lines = len(text.splitlines())
        # Average reading speed: 200 words per minute
        reading_mins = math.ceil(len(words) / 200) if words else 0

        return {
            "words": len(words),
            "chars": chars,
            "chars_no_spaces": chars_no_spaces,
            "lines": lines,
            "reading_time_mins": reading_mins,
        }

    @staticmethod
    def extract_outline(text: str) -> List[Dict[str, Any]]:
        """Extract headers as structured outline for navigation."""
        outline = []
        lines = text.splitlines()
        heading_regex = re.compile(r"^(#{1,6})\s+(.+)$")

        for idx, line in enumerate(lines):
            match = heading_regex.match(line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                outline.append({
                    "line": idx + 1,
                    "level": level,
                    "title": title,
                })
        return outline

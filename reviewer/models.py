from __future__ import annotations

from dataclasses import dataclass, field

SEVERITIES = ["info", "low", "medium", "high"]
CATEGORIES = ["security", "correctness", "error_handling", "reliability", "performance",
              "maintainability", "testing", "logic"]


@dataclass
class Finding:
    file: str
    line: int
    severity: str          # info | low | medium | high
    category: str
    rule: str              # e.g. PY001 or llm
    message: str
    suggestion: str = ""
    source: str = "static"  # static | llm | tests
    confidence: float = 1.0

    def key(self) -> tuple:
        return (self.file, self.line, self.category)


@dataclass
class TestRecommendation:
    file: str
    function: str
    line: int
    reason: str
    cases: list[str] = field(default_factory=list)

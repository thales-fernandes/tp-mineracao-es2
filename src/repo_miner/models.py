from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class HistoryMetrics:
    path: str
    commits: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    last_modified: datetime | None = None

    @property
    def churn(self) -> int:
        return self.lines_added + self.lines_deleted


@dataclass(slots=True)
class StaticMetrics:
    path: str
    nloc: int = 0
    function_count: int = 0
    total_complexity: int = 0
    max_complexity: int = 0
    dependency_count: int = 0

    @property
    def average_complexity(self) -> float:
        if self.function_count == 0:
            return 0.0
        return self.total_complexity / self.function_count


@dataclass(slots=True)
class FilePriority:
    path: str
    score: float
    classification: str
    history: HistoryMetrics
    static: StaticMetrics

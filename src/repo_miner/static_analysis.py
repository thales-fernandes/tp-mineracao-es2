from __future__ import annotations

from pathlib import Path

import lizard

from .dependencies import count_dependencies, is_code_file
from .models import StaticMetrics


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}


def collect_static_metrics(repo_path: Path) -> dict[str, StaticMetrics]:
    metrics: dict[str, StaticMetrics] = {}

    for file_path in _iter_code_files(repo_path):
        relative_path = file_path.relative_to(repo_path).as_posix()
        analysis = lizard.analyze_file(str(file_path))
        function_complexities = [function.cyclomatic_complexity for function in analysis.function_list]
        metrics[relative_path] = StaticMetrics(
            path=relative_path,
            nloc=analysis.nloc,
            function_count=len(analysis.function_list),
            total_complexity=sum(function_complexities),
            max_complexity=max(function_complexities, default=0),
            dependency_count=count_dependencies(file_path),
        )

    return metrics


def _iter_code_files(repo_path: Path):
    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(repo_path).parts):
            continue
        if is_code_file(path):
            yield path

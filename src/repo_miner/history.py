from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from pydriller import Repository

from .models import HistoryMetrics


def collect_history_metrics(repo_path: Path) -> dict[str, HistoryMetrics]:
    metrics: dict[str, HistoryMetrics] = defaultdict(lambda: HistoryMetrics(path=""))

    for commit in Repository(str(repo_path)).traverse_commits():
        for modified_file in commit.modified_files:
            path = modified_file.new_path or modified_file.old_path
            if not path:
                continue

            item = metrics[path]
            item.path = path
            item.commits += 1
            item.lines_added += modified_file.added_lines or 0
            item.lines_deleted += modified_file.deleted_lines or 0
            item.last_modified = commit.committer_date

    return dict(metrics)

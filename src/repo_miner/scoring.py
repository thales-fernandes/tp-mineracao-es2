from __future__ import annotations

from .models import FilePriority, HistoryMetrics, StaticMetrics


def calculate_priorities(
    history_metrics: dict[str, HistoryMetrics],
    static_metrics: dict[str, StaticMetrics],
) -> list[FilePriority]:
    paths = sorted(set(history_metrics) | set(static_metrics))

    max_commits = _max_value((history_metrics.get(path, HistoryMetrics(path)).commits for path in paths))
    max_churn = _max_value((history_metrics.get(path, HistoryMetrics(path)).churn for path in paths))
    max_complexity = _max_value((static_metrics.get(path, StaticMetrics(path)).total_complexity for path in paths))
    max_dependencies = _max_value((static_metrics.get(path, StaticMetrics(path)).dependency_count for path in paths))

    priorities: list[FilePriority] = []
    for path in paths:
        history = history_metrics.get(path, HistoryMetrics(path=path))
        static = static_metrics.get(path, StaticMetrics(path=path))

        change_score = _normalize(history.commits, max_commits)
        churn_score = _normalize(history.churn, max_churn)
        complexity_score = _normalize(static.total_complexity, max_complexity)
        dependency_score = _normalize(static.dependency_count, max_dependencies)

        score = (
            change_score * 0.40
            + complexity_score * 0.30
            + dependency_score * 0.20
            + churn_score * 0.10
        )

        priorities.append(
            FilePriority(
                path=path,
                score=round(score * 100, 2),
                classification=_classify(score),
                history=history,
                static=static,
            )
        )

    return sorted(priorities, key=lambda item: item.score, reverse=True)


def _max_value(values) -> float:
    return max(values, default=0) or 1


def _normalize(value: float, maximum: float) -> float:
    if maximum <= 0:
        return 0.0
    return value / maximum


def _classify(score: float) -> str:
    if score >= 0.70:
        return "alta"
    if score >= 0.40:
        return "media"
    return "baixa"

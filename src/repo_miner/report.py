from __future__ import annotations

import csv
import json
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table

from .models import FilePriority


def print_summary(priorities: list[FilePriority]) -> None:
    total_files = len(priorities)
    high_priority = sum(1 for item in priorities if item.classification == "alta")
    medium_priority = sum(1 for item in priorities if item.classification == "media")
    total_commits = sum(item.history.commits for item in priorities)
    total_churn = sum(item.history.churn for item in priorities)
    total_complexity = sum(item.static.total_complexity for item in priorities)
    total_dependencies = sum(item.static.dependency_count for item in priorities)

    summary = (
        f"[bold]Arquivos analisados:[/bold] {total_files}\n"
        f"[bold red]Prioridade alta:[/bold red] {high_priority}    "
        f"[bold yellow]media:[/bold yellow] {medium_priority}\n"
        f"[bold]Commits em arquivos analisados:[/bold] {total_commits}\n"
        f"[bold]Churn total:[/bold] {total_churn} linhas\n"
        f"[bold]Complexidade total:[/bold] {total_complexity}\n"
        f"[bold]Dependencias detectadas:[/bold] {total_dependencies}"
    )
    Console().print(Panel(summary, title="Resumo executivo", border_style="cyan"))


def print_table(priorities: list[FilePriority], limit: int) -> None:
    table = Table(
        title="Ranking de prioridade de refatoracao",
        box=box.SIMPLE_HEAVY,
        expand=True,
        show_lines=False,
    )
    table.add_column("#", justify="right", width=3)
    table.add_column("Arquivo", ratio=4, overflow="fold")
    table.add_column("Score", justify="right", width=8)
    table.add_column("Prioridade", width=10)
    table.add_column("Sinais", ratio=2)
    table.add_column("Recomendacao", ratio=3)

    for index, item in enumerate(priorities[:limit], start=1):
        table.add_row(
            str(index),
            item.path,
            f"{item.score:.2f}",
            _classification_label(item.classification),
            _signals(item),
            recommendation_for(item),
        )

    Console().print(table)


def print_hotspots(priorities: list[FilePriority], limit: int = 5) -> None:
    console = Console()
    if not priorities:
        return

    table = Table.grid(expand=True)
    table.add_column(ratio=3)
    table.add_column(ratio=2)
    max_score = max((item.score for item in priorities), default=1) or 1

    for item in priorities[:limit]:
        bar = ProgressBar(total=max_score, completed=item.score, width=34)
        details = (
            f"[bold]{item.path}[/bold]\n"
            f"{_classification_label(item.classification)}  "
            f"score [bold]{item.score:.2f}[/bold]  "
            f"commits {item.history.commits}  "
            f"churn {item.history.churn}  "
            f"CC {item.static.total_complexity}  "
            f"deps {item.static.dependency_count}\n"
            f"[dim]{recommendation_for(item)}[/dim]"
        )
        table.add_row(details, bar)

    console.print(Panel(table, title="Hotspots principais", border_style="green"))


def write_json(priorities: list[FilePriority], output_path: Path) -> None:
    output_path.write_text(
        json.dumps([_to_dict(item) for item in priorities], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_csv(priorities: list[FilePriority], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(_to_dict(priorities[0]).keys()) if priorities else [])
        if not priorities:
            return
        writer.writeheader()
        for item in priorities:
            writer.writerow(_to_dict(item))


def recommendation_for(item: FilePriority) -> str:
    reasons: list[str] = []
    if item.history.commits > 0:
        reasons.append("muda com frequencia")
    if item.static.total_complexity >= 10 or item.static.max_complexity >= 8:
        reasons.append("complexidade alta")
    if item.static.dependency_count >= 5:
        reasons.append("muitas dependencias")
    if item.history.churn >= 100:
        reasons.append("alto churn")
    if not reasons:
        return "monitorar"
    return "refatorar: " + ", ".join(reasons[:2])


def _classification_label(classification: str) -> str:
    if classification == "alta":
        return "[bold red]alta[/bold red]"
    if classification == "media":
        return "[bold yellow]media[/bold yellow]"
    return "[green]baixa[/green]"


def _signals(item: FilePriority) -> str:
    return (
        f"commits {item.history.commits}\n"
        f"churn {item.history.churn}\n"
        f"CC {item.static.total_complexity}/{item.static.max_complexity}\n"
        f"deps {item.static.dependency_count}"
    )


def _to_dict(item: FilePriority) -> dict[str, object]:
    return {
        "path": item.path,
        "score": item.score,
        "classification": item.classification,
        "recommendation": recommendation_for(item),
        "commits": item.history.commits,
        "lines_added": item.history.lines_added,
        "lines_deleted": item.history.lines_deleted,
        "churn": item.history.churn,
        "last_modified": item.history.last_modified.isoformat() if item.history.last_modified else None,
        "nloc": item.static.nloc,
        "function_count": item.static.function_count,
        "total_complexity": item.static.total_complexity,
        "max_complexity": item.static.max_complexity,
        "average_complexity": round(item.static.average_complexity, 2),
        "dependency_count": item.static.dependency_count,
    }

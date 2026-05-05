from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from .history import collect_history_metrics
from .report import print_hotspots, print_summary, print_table, write_csv, write_json
from .scoring import calculate_priorities
from .static_analysis import collect_static_metrics

app = typer.Typer(help="Analisa repositorios Git e prioriza arquivos para refatoracao.")
console = Console()


@app.callback()
def main() -> None:
    """Ferramenta de mineracao de repositorios."""


@app.command()
def analyze(
    repo: Annotated[
        Path,
        typer.Argument(help="Caminho do repositorio Git a ser analisado."),
    ] = Path("."),
    limit: Annotated[int, typer.Option("--limit", "-l", help="Quantidade de arquivos exibidos.")] = 15,
    hotspots: Annotated[int, typer.Option("--hotspots", "-h", help="Quantidade de hotspots destacados.")] = 5,
    min_score: Annotated[
        float,
        typer.Option("--min-score", help="Score minimo exibido no ranking, de 0 a 100."),
    ] = 0.0,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Arquivo de saida .json ou .csv."),
    ] = None,
) -> None:
    """Cruza frequencia de alteracoes, complexidade e dependencias."""
    _run_analysis(repo=repo, limit=limit, hotspots=hotspots, min_score=min_score, output=output)


@app.command()
def wizard() -> None:
    """Executa a analise em modo guiado pelo terminal."""
    console.print(
        Panel(
            "Responda poucas perguntas e a ferramenta monta o ranking de refatoracao.",
            title="Modo guiado",
            border_style="cyan",
        )
    )
    repo = Path(typer.prompt("Caminho do repositorio", default="."))
    limit = typer.prompt("Quantos arquivos mostrar no ranking", default=15, type=int)
    hotspots = typer.prompt("Quantos hotspots destacar", default=5, type=int)
    min_score = typer.prompt("Score minimo exibido", default=0.0, type=float)
    output_text = typer.prompt("Salvar relatorio em JSON/CSV? Informe caminho ou deixe vazio", default="")
    output = Path(output_text) if output_text.strip() else None
    _run_analysis(repo=repo, limit=limit, hotspots=hotspots, min_score=min_score, output=output)


def _run_analysis(repo: Path, limit: int, hotspots: int, min_score: float, output: Path | None) -> None:
    repo = repo.resolve()
    if not repo.exists():
        raise typer.BadParameter(f"Repositorio nao encontrado: {repo}")
    if not (repo / ".git").exists():
        raise typer.BadParameter(f"O caminho informado nao parece ser um repositorio Git: {repo}")
    if not 0 <= min_score <= 100:
        raise typer.BadParameter("--min-score deve ficar entre 0 e 100")

    console.rule("[bold cyan]Repo Miner")
    console.print(f"[bold]Repositorio:[/bold] {repo}")

    try:
        with console.status("Minerando historico Git com PyDriller..."):
            history_metrics = collect_history_metrics(repo)
    except OSError as exc:
        raise typer.ClickException(
            "Nao foi possivel acessar o historico Git. "
            "Verifique permissoes de escrita/leitura no diretorio .git e tente novamente."
        ) from exc

    with console.status("Calculando metricas estaticas..."):
        static_metrics = collect_static_metrics(repo)

    priorities = calculate_priorities(history_metrics, static_metrics)
    priorities = [item for item in priorities if item.score >= min_score]
    if not priorities:
        console.print("[yellow]Nenhum arquivo analisavel foi encontrado.[/yellow]")
        return

    print_summary(priorities)
    print_hotspots(priorities, hotspots)
    print_table(priorities, limit)

    if output:
        output = output.resolve()
        if output.suffix.lower() == ".json":
            write_json(priorities, output)
        elif output.suffix.lower() == ".csv":
            write_csv(priorities, output)
        else:
            raise typer.BadParameter("A saida deve ter extensao .json ou .csv")
        console.print(f"[green]Relatorio salvo em:[/green] {output}")


if __name__ == "__main__":
    app()

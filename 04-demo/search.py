"""
Interactive semantic search CLI for the RavenDB ProductsDemo.

Usage:
    python search.py                    # interactive mode
    python search.py "warm winter coat" # single query mode

How it works:
    RavenDB 7.0 ships with a built-in embedding model (bge-micro-v2).
    When you call vector.search() on a text field, RavenDB generates the
    query embedding on the fly and compares it against all document embeddings
    using an HNSW (Hierarchical Navigable Small World) approximate nearest
    neighbour graph built by the Corax indexing engine.

    The result: natural language queries that find semantically similar
    products even when they share no keywords with the query.
"""

import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from config import get_store
from models import Product

console = Console()

# ─── RQL query ──────────────────────────────────────────────────────────────
#
# vector.search(Description, $query) instructs RavenDB to:
#   1. Generate an embedding for $query using bge-micro-v2 (built-in, no API key)
#   2. Search the HNSW graph index on the Description field
#   3. Return the closest matches by cosine similarity
#
# Combining vector search with a structured filter (Category) in a single query
# is one of RavenDB's key advantages over standalone vector stores.
#
SEMANTIC_QUERY = """
from Products
where vector.search(Description, $query)
order by score() desc
limit $limit
"""

SEMANTIC_QUERY_WITH_CATEGORY = """
from Products
where vector.search(Description, $query)
and Category = $category
order by score() desc
limit $limit
"""


def run_search(
    query_text: str,
    limit: int = 5,
    category: Optional[str] = None,
) -> list[Product]:
    """Execute a semantic search and return matching Product documents."""
    store = get_store()

    with store.open_session() as session:
        if category:
            rql = SEMANTIC_QUERY_WITH_CATEGORY
        else:
            rql = SEMANTIC_QUERY

        raw = (
            session.advanced.raw_query(rql, Product)
            .add_parameter("query", query_text)
            .add_parameter("limit", limit)
        )

        if category:
            raw = raw.add_parameter("category", category)

        return list(raw)


def display_results(query: str, results: list[Product], category: Optional[str] = None) -> None:
    """Render search results as a Rich table."""
    filter_label = f" · category: [italic]{category}[/italic]" if category else ""
    console.print(
        Panel(
            f'[bold cyan]"{query}"[/bold cyan]{filter_label}',
            title="[bold]Semantic Search Query[/bold]",
            border_style="blue",
        )
    )

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Product", style="bold", min_width=30)
    table.add_column("Category", style="cyan", min_width=12)
    table.add_column("Price", justify="right", style="green")
    table.add_column("Description", style="dim", max_width=55)

    for i, product in enumerate(results, start=1):
        # Truncate description for display
        desc = product.description
        if len(desc) > 120:
            desc = desc[:117] + "..."

        table.add_row(
            str(i),
            product.name,
            product.category,
            f"${product.price:,.2f}",
            desc,
        )

    console.print(table)
    console.print(f"[dim]Returned {len(results)} result(s)[/dim]\n")


def print_example_queries() -> None:
    """Print example queries that show semantic search in action."""
    examples = [
        ("something warm for winter travel", None),
        ("peripheral for heavy typists", None),
        ("relieve back pain at my desk", None),
        ("drink coffee without electricity", None),
        ("reduce noise while concentrating", None),
        ("powerful portable power for camping", None),
        ("track fitness and heart rate accurately", None),
        ("lightweight shelter for multi-day hiking", None),
        ("books for becoming a better programmer", None),
        ("warm winter coat", "Clothing"),          # with category filter
        ("muscle recovery after running", "Fitness"),
    ]

    console.print(
        Panel(
            "\n".join(
                f'  [cyan]python search.py [bold]"{q}"[/bold][/cyan]'
                + (f' [dim]--category "{c}"[/dim]' if c else "")
                for q, c in examples
            ),
            title="[bold]Example queries[/bold]",
            subtitle="[dim]These use no shared keywords with the matching products[/dim]",
            border_style="green",
        )
    )


def interactive_mode() -> None:
    """Run an interactive REPL for semantic search."""
    console.rule("[bold blue]RavenDB Semantic Search Demo[/bold blue]")
    console.print(
        "Powered by [bold]RavenDB 7.0[/bold] · bge-micro-v2 built-in embeddings · HNSW via Corax\n"
    )
    print_example_queries()

    console.print("\nType a natural language query. Press [bold]Ctrl+C[/bold] or enter [bold]q[/bold] to quit.\n")

    while True:
        try:
            query = console.input("[bold green]Search >[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not query or query.lower() in {"q", "quit", "exit"}:
            console.print("[dim]Goodbye.[/dim]")
            break

        results = run_search(query)
        display_results(query, results)


def main() -> None:
    args = sys.argv[1:]

    # Parse optional --category flag
    category = None
    if "--category" in args:
        idx = args.index("--category")
        if idx + 1 < len(args):
            category = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

    if args:
        # Single query mode: python search.py "query text"
        query = " ".join(args)
        results = run_search(query, category=category)
        display_results(query, results, category=category)
    else:
        # Interactive REPL mode
        interactive_mode()


if __name__ == "__main__":
    main()

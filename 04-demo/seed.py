"""
Seed script — loads 50 products from data/products.json into RavenDB.

Usage:
    python seed.py

This only needs to be run once. Running it again is safe — it uses the
document IDs from the JSON file, so no duplicates will be created.
"""

import json
import os
from pathlib import Path

from rich.console import Console
from rich.progress import track

from config import get_store
from models import Product

console = Console()

DATA_FILE = Path(__file__).parent / "data" / "products.json"


def seed_database() -> None:
    console.rule("[bold blue]RavenDB Semantic Search — Seed Script[/bold blue]")

    # Load product data
    if not DATA_FILE.exists():
        console.print(f"[red]✗ Data file not found:[/red] {DATA_FILE}")
        raise SystemExit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_products = json.load(f)

    console.print(f"[green]✓[/green] Loaded [bold]{len(raw_products)}[/bold] products from [cyan]{DATA_FILE.name}[/cyan]")

    # Connect to RavenDB
    console.print(f"\nConnecting to RavenDB...")
    store = get_store()
    console.print(f"[green]✓[/green] Connected to [bold]{store.urls[0]}[/bold] / [bold]{store.database}[/bold]")

    # Bulk insert products
    console.print("\nInserting products...")
    inserted = 0
    skipped = 0

    with store.bulk_insert() as bulk:
        for raw in track(raw_products, description="Seeding products"):
            product = Product(
                name=raw["name"],
                category=raw["category"],
                price=raw["price"],
                description=raw["description"],
            )
            # Use the ID from the JSON so re-running is idempotent
            bulk.store_as(product, raw["id"])
            inserted += 1

    console.print(f"\n[green]✓[/green] Inserted [bold]{inserted}[/bold] products into RavenDB.")
    console.print(
        "\n[yellow]Note:[/yellow] Vector indexes are built asynchronously. "
        "Wait a few seconds before running search.py for the first time."
    )
    console.print("\n[bold]All done! Run [cyan]python search.py[/cyan] to start searching.[/bold]")


if __name__ == "__main__":
    seed_database()

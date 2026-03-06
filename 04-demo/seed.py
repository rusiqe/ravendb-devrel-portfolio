"""
Seed script — loads 50 products from data/products.json into RavenDB,
pre-computing a bge-micro-v2 embedding for each product description.

Usage:
    python seed.py

This only needs to be run once. Running it again is safe — it uses the
document IDs from the JSON file, so no duplicates will be created.

Embeddings are generated using the same bge-micro-v2 ONNX model bundled
inside RavenDB, so they are fully compatible with RavenDB's vector indexes.
No API key. No external service. Nothing to configure.
"""

import json
from pathlib import Path

from rich.console import Console
from rich.progress import track

from config import get_store
from embedder import embed_to_base64
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

    # Pre-warm the embedding model once before the bulk loop
    console.print("\nLoading bge-micro-v2 embedding model (first run only)...")
    embed_to_base64("warmup")
    console.print("[green]✓[/green] Embedding model ready\n")

    # Bulk insert products with pre-computed embeddings
    console.print("Generating embeddings and inserting products...")
    inserted = 0

    with store.bulk_insert() as bulk:
        for raw in track(raw_products, description="Seeding products"):
            # Generate a 384-dim bge-micro-v2 embedding for the description
            embedding = embed_to_base64(raw["description"])

            product = Product(
                name=raw["name"],
                category=raw["category"],
                price=raw["price"],
                description=raw["description"],
                descriptionVector=embedding,
            )
            # Use the ID from the JSON so re-running is idempotent
            bulk.store_as(product, raw["id"])
            inserted += 1

    console.print(f"\n[green]✓[/green] Inserted [bold]{inserted}[/bold] products with embeddings into RavenDB.")
    console.print(
        "\n[dim]Each document now carries a [bold]descriptionVector[/bold] field — "
        "a 384-dim bge-micro-v2 embedding of its description. "
        "RavenDB builds an HNSW graph index over these automatically.[/dim]"
    )
    console.print("\n[bold]All done! Run [cyan]python search.py[/cyan] to start searching.[/bold]")


if __name__ == "__main__":
    seed_database()

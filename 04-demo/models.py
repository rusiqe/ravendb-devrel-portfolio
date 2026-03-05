"""
Domain model for the ProductsDemo database.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    """
    A product document stored in RavenDB.

    The `description` field is what RavenDB will generate embeddings for
    when vector.search() queries are issued. With RavenDB 7.0+, the built-in
    bge-micro-v2 model handles embedding generation automatically — no
    external API keys or services required.
    """

    name: str
    category: str
    price: float
    description: str
    id: Optional[str] = field(default=None)

    def __repr__(self) -> str:
        return f"Product(name={self.name!r}, category={self.category!r}, price={self.price})"

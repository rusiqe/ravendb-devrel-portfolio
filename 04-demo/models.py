"""
Domain model for the ProductsDemo database.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    """
    A product document stored in RavenDB.

    The `descriptionVector` field stores a pre-computed 384-dim bge-micro-v2
    embedding (base64-encoded float32 array) for the product description.
    Seed.py generates these using the same model bundled inside RavenDB,
    so they are fully compatible with any static vector index you define later.

    The vector field is stored alongside the document — no separate system,
    no schema changes, no sync jobs. Exactly as described in the blog post.
    """

    name: str
    category: str
    price: float
    description: str
    descriptionVector: Optional[str] = field(default=None)  # base64 float32 embedding
    id: Optional[str] = field(default=None)

    def __repr__(self) -> str:
        return f"Product(name={self.name!r}, category={self.category!r}, price={self.price})"

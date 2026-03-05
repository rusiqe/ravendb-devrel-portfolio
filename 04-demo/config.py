"""
Configuration loader for the RavenDB Semantic Search demo.
Reads from a .env file (copy .env.example to .env and fill in your values).
"""

import os
from dotenv import load_dotenv
from ravendb import DocumentStore

load_dotenv()

RAVENDB_URL = os.getenv("RAVENDB_URL", "http://localhost:8080")
RAVENDB_DATABASE = os.getenv("RAVENDB_DATABASE", "ProductsDemo")
RAVENDB_CERT_PATH = os.getenv("RAVENDB_CERT_PATH", None)


def get_store() -> DocumentStore:
    """
    Create and initialize a RavenDB DocumentStore.

    For RavenDB Cloud: set RAVENDB_CERT_PATH to your downloaded .pem certificate.
    For local Docker:  leave RAVENDB_CERT_PATH empty — no certificate needed.
    """
    store = DocumentStore(urls=[RAVENDB_URL], database=RAVENDB_DATABASE)

    if RAVENDB_CERT_PATH and os.path.exists(RAVENDB_CERT_PATH):
        store.certificate_pem_path = RAVENDB_CERT_PATH

    store.initialize()
    return store

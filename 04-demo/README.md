# RavenDB Semantic Search — Product Catalog Demo

A minimal but complete Python demo showing RavenDB 7.0's built-in vector search in action.

**The core idea:** search a 50-product catalog using natural language — no shared keywords required. Ask for _"something warm for winter travel"_ and get the insulated parka. Ask for _"relieve back pain at my desk"_ and get the lumbar support pillow. Ask for _"drink coffee without electricity"_ and get the French press.

This is what semantic search does that keyword search cannot. And with RavenDB 7.0, it requires zero additional infrastructure.

---

## How it works

RavenDB 7.0 ships with a built-in embedding model — **bge-micro-v2** — that runs inside the database process. When you call `vector.search()` on a text field, RavenDB:

1. Generates an embedding for your query using bge-micro-v2 (no API key, no network call)
2. Searches the **HNSW graph** (Hierarchical Navigable Small World) index built by the **Corax** indexing engine
3. Returns the nearest neighbours by cosine similarity

The query looks like this:

```sql
from Products
where vector.search(Description, $query)
order by score() desc
limit 5
```

You can also combine vector search with structured filters in a single query — no joining across systems:

```sql
from Products
where vector.search(Description, $query)
and Category = $category
order by score() desc
limit 5
```

---

## Prerequisites

- Python 3.11+
- A RavenDB 7.0+ instance ([RavenDB Cloud free tier](https://cloud.ravendb.net) or local Docker)

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/rusiqe/ravendb-devrel-portfolio.git
cd ravendb-devrel-portfolio/04-demo
pip install -r requirements.txt
```

### 2. Configure your RavenDB connection

```bash
cp .env.example .env
```

Edit `.env` with your cluster details:

```env
RAVENDB_URL=https://your-cluster.ravendb.cloud
RAVENDB_DATABASE=ProductsDemo
RAVENDB_CERT_PATH=./ravendb-client.pem
```

**Getting a RavenDB Cloud certificate:**
1. Go to [cloud.ravendb.net](https://cloud.ravendb.net) → create a free cluster
2. Cluster dashboard → **Manage** → **Client Certificate** → **Generate**
3. Download the `.pem` file and place it in the `04-demo/` directory

For a **local Docker instance** (no certificate needed):
```bash
docker run -d -p 8080:8080 -p 38888:38888 ravendb/ravendb
```
Then set `RAVENDB_URL=http://localhost:8080` and leave `RAVENDB_CERT_PATH` empty.

### 3. Seed the database

```bash
python seed.py
```

This loads 50 products across Electronics, Clothing, Kitchen, Fitness, Outdoors, and Books categories. Wait a few seconds for RavenDB to build the vector index before searching.

---

## Usage

### Interactive mode

```bash
python search.py
```

Type any natural language query at the prompt. The results will show the most semantically similar products even when they share no keywords with your query.

### Single query mode

```bash
python search.py "something warm for winter travel"
python search.py "relieve back pain at my desk"
python search.py "peripheral for heavy typists"
python search.py "portable power source for off-grid work"
```

### Filter by category

```bash
python search.py "warm winter coat" --category Clothing
python search.py "muscle recovery after running" --category Fitness
```

---

## Example: keyword search vs. semantic search

The query `"something to keep warm in winter"` contains none of the words in the Canada Goose parka description. A keyword search returns zero results. RavenDB's vector search returns the parka at the top — because the *meaning* is close, even if the words aren't.

| Query | Keyword search | Semantic search (RavenDB) |
|---|---|---|
| "something warm for winter travel" | 0 results | Expedition Parka, Merino Base Layer |
| "relieve back pain at my desk" | 0 results | Lumbar Support Pillow, Monitor Arm |
| "drink coffee without electricity" | 0 results | French Press |
| "peripheral for heavy typists" | 0 results | Mechanical Keyboard |
| "muscle recovery after a run" | 0 results | Foam Roller, Resistance Bands |

---

## Project structure

```
04-demo/
├── config.py           # DocumentStore factory, reads from .env
├── models.py           # Product dataclass
├── seed.py             # Bulk-insert 50 products into RavenDB
├── search.py           # Semantic search CLI (interactive + single query)
├── requirements.txt
├── .env.example
└── data/
    └── products.json   # 50 products with rich descriptions
```

---

## Further reading

- [RavenDB Vector Search Overview](https://ravendb.net/docs/article-page/latest/csharp/ai-integration/vector-search/overview)
- [Vector Search with Static Indexes](https://ravendb.net/docs/article-page/latest/csharp/ai-integration/vector-search/vector-search-using-static-index)
- [bge-micro-v2 built-in model](https://ravendb.net/articles/new-in-7-0-ravendbs-vector-search)
- [Blog post: Your Database Already Has a Vector Search Engine](../03-content/blog-post.md)

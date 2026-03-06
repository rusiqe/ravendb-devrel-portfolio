# Your Database Already Has a Vector Search Engine. You Just Haven't Used It Yet.

Most developers bolt on a vector store after the fact. An afterthought after discovering how the default search experience leaves out the fun of discovery and suggestion. Pinecone here, Weaviate there, a sync job duct-taped in between. It works (sometimes) until it just doesn't. Here's a better way.


## The Problem With Keyword Search

Let's be honest about what traditional search actually does: it matches characters. If you search for "fast," you get back documents that contain the string "fast." That's the whole trick.

Which is fine until you realize that "high-performance," "low-latency," and "quick processing pipelines" all mean roughly the same thing, and keyword search has no idea. It won't connect those dots. It's not stupid, it's just operating on the wrong abstraction.

That's the gap semantic search fills.

Semantic search works on *meaning*, not words. The mechanism that makes this possible is something called an **embedding**.


## What Embeddings Are

An embedding represents text as a list of numbers, a vector, that encodes what that text *means* rather than how it's spelled. Feed "fast car" and "high-speed vehicle" into a good embedding model, and you'll get back two vectors that sit close to each other in multi-dimensional space. Feed in "fast car" and "tax policy," and those vectors will be far apart.

That distance becomes your search signal. Instead of asking "does this document contain this word?", you're asking "is this document *close in meaning* to my query?"

That's the shift from keyword search to semantic search. Simple concept; the implementation is what gets interesting.


## How RavenDB Implements Vector Search
![RavenDB Vector Search](https://imgur.com/a/B5avv7Y)

Starting with **RavenDB 7.0**, vector search is built directly into the database. Not a plugin. Not a sidecar. It's part of the core indexing engine.

Under the hood, RavenDB uses **Corax**, its indexing engine, to build an **HNSW graph** (Hierarchical Navigable Small World). HNSW is among the strongest algorithms for approximate nearest neighbor search. It scales to millions of vectors and doesn't require loading everything into memory.

You get vector search where your data already lives. No sync jobs, no consistency headaches, no extra infrastructure.

---

## Where Embeddings Come From

Before looking at queries, it helps to first understand how RavenDB generates embeddings. When defining a static index, you configure the embedding provider once, and RavenDB handles generation and updates from that point on. It integrates with:

- **OpenAI** (text-embedding-3-small, text-embedding-3-large, etc.)
- **Azure OpenAI**
- **Hugging Face**
- **Google AI**
- **Ollama** (for local models)
- **Mistral**

The most interesting option, though, requires none of these. RavenDB ships with **bge-micro-v2** built in. It's a compact embedding model that runs entirely inside the database process. No API key. No network call. No rate limits. If you want semantic search today, you can have it without signing up for anything else or creating a data storage stack.

For internal search, smaller datasets, or privacy-sensitive applications, it's all you need.

---

## Two Ways to Query

There are two ways to run vector search in RavenDB, and they serve different purposes.

### Dynamic Queries

The fast path. Write a query, and RavenDB creates the index automatically. Works great for prototyping and exploration:

```rql
from Products
where vector.search(Description, "high performance computing solutions")
```

Embedding generation and index creation happen behind the scenes. You just write the query.

### Static Indexes

For explicit control, define your vector field upfront, configure the HNSW parameters, and get predictable production performance:

```rql
from index 'Products/ByDescriptionVector'
where vector.search(DescriptionVector, $query, 0.75)
order by score() desc
limit 10
```

Static indexes also support mixing vector search with structured filters in a single query:

```rql
from index 'Products/ByDescriptionVector'
where vector.search(DescriptionVector, $query, 0.8)
and Category = "Electronics"
and Price between 50 and 500
order by score() desc
```

Semantic relevance combined with hard filters, one query, one system. That's the one that matters for real applications.

---

## The Operational Argument

The standard approach to adding vector search goes like this: spin up a separate vector database, write a sync pipeline, figure out how to keep both systems consistent, then manage that forever.

That's a real maintenance burden. Two systems means two failure modes, two scaling strategies, and eventual consistency problems that surface at the worst time.

With RavenDB, your operational database *is* your vector store. When a document updates, the vector index updates. You're not orchestrating two systems — you're running one. That matters most in:

- **Search engines** — semantic relevance over your own content
- **Recommendation systems** — find items similar to what a user engaged with
- **RAG pipelines** — retrieve the right context chunks before sending to an LLM

In all of these scenarios, you want your retrieval layer next to your data, not three network hops away.

---

## Building With It

To see this in practice, I built a [product catalog demo](https://github.com/rusiqe/ravendb-devrel-portfolio/tree/main/04-demo) — 50 products seeded into RavenDB, searchable via a Python CLI using `vector.search()` with the built-in bge-micro-v2 model.

On the Python side, the RavenDB client exposes raw RQL through `session.advanced.raw_query()`. The whole search function is lean ([full source](https://github.com/rusiqe/ravendb-devrel-portfolio/blob/main/04-demo/search.py)):

```python
with store.open_session() as session:
    results = list(
        session.advanced.raw_query(
            """
            from Products
            where vector.search(Description, $query)
            order by score() desc
            limit $limit
            """,
            Product,
        )
        .add_parameter("query", query_text)
        .add_parameter("limit", 5)
    )
```

No embedding library. No separate vector client. The same session interface used for any other RavenDB query. Adding a category filter is one extra `and` clause in the RQL — the structured filter and vector search execute together inside RavenDB, no post-filtering on the client.

Seeding the data is just a bulk insert ([seed.py](https://github.com/rusiqe/ravendb-devrel-portfolio/blob/main/04-demo/seed.py)). No schema changes, no pre-computation step:

```python
with store.bulk_insert() as bulk:
    for product in products:
        bulk.store_as(product, product.id)
```

The revealing part was running queries that share zero words with their matching products:

| Query | Keyword result | Semantic result (RavenDB) |
|---|---|---|
| "something warm for winter travel" | 0 results | Canada Goose Expedition Parka |
| "relieve back pain at my desk" | 0 results | Lumbar Support Pillow, Monitor Arm |
| "drink coffee without electricity" | 0 results | Bodum Chambord French Press |
| "peripheral for heavy typists" | 0 results | Keychron K2 Mechanical Keyboard |
| "muscle recovery after a run" | 0 results | TriggerPoint Foam Roller |
| "books for becoming a better programmer" | 0 results | Clean Code, Designing Data-Intensive Apps |

Every query in that table is something a real user would type. None of them share a single word with the product description that matched. That's the gap keyword search leaves open, and it's sitting right there in your existing data.

Clone the demo and have it running in under five minutes: [github.com/rusiqe/ravendb-devrel-portfolio/tree/main/04-demo](https://github.com/rusiqe/ravendb-devrel-portfolio/tree/main/04-demo).

---

## Try It

If you're on RavenDB 7.0, a dynamic query is enough to get started — no index configuration required. The [RavenDB docs on vector search](https://ravendb.net/docs) cover static indexes and embedding provider configuration when you're ready to go further.

The infrastructure question is already answered. What are you going to build with it?

---

*Taurai is a technical writer and DevRel engineer. Find more at [taurai.eu](https://www.taurai.eu)*

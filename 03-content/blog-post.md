# Your Database Already Has a Vector Search Engine. You Just Haven't Used It Yet.

Most developers bolt on a vector store after the fact. Pinecone here, Weaviate there, a sync job duct-taped in between. It works — until it doesn't. Here's a better way.

---

## The Problem With Keyword Search

Let's be honest about what traditional search actually does: it matches characters. You search for "fast," you get back documents that contain the string "fast." That's the whole trick.

Which is fine — until you realize that "high-performance," "low-latency," and "quick processing pipelines" all mean roughly the same thing, and keyword search has absolutely no idea. It won't connect those dots for you. It's not stupid, it's just operating on the wrong abstraction.

That's the gap semantic search fills.

Semantic search works on *meaning*, not *words*. And the mechanism that makes that possible is something called an **embedding**.

---

## What Embeddings Actually Are

An embedding is a way of representing text as a list of numbers — a vector — that encodes what that text *means* rather than how it's spelled. Feed "fast car" and "high-speed vehicle" into a good embedding model, and you'll get back two vectors that are close to each other in multi-dimensional space. Feed in "fast car" and "tax policy," and those vectors will be far apart.

That distance becomes your search signal. Instead of asking "does this document contain this word?", you're asking "is this document *close in meaning* to my query?"

That's the shift from keyword search to semantic search. It's conceptually simple. The implementation is where things get interesting.

---

## How RavenDB Does It

Starting with **RavenDB 7.0**, vector search is built directly into the database. Not as a plugin. Not as a sidecar. It's part of the core indexing engine.

Under the hood, RavenDB uses **Corax** — its indexing engine — to build an **HNSW graph** (Hierarchical Navigable Small World). HNSW is one of the best-performing algorithms for approximate nearest neighbor search. It's fast, it scales to millions of vectors, and it doesn't require you to load everything into memory.

The result: you get vector search where your data already lives. No sync jobs. No consistency headaches. No extra infrastructure to manage.

---

## Dynamic Queries vs. Static Indexes

There are two ways to use vector search in RavenDB, and they serve different purposes.

### Dynamic Queries

The fast path. Write a query, RavenDB creates the index automatically. Great for prototyping and exploration:

```rql
from Products
where vector.search(Description, "high performance computing solutions")
```

RavenDB handles the embedding generation and index creation behind the scenes. You just write the query.

### Static Indexes

When you want explicit control — define your vector field up front, configure the HNSW parameters, and get predictable, production-ready performance:

```rql
from index 'Products/ByDescriptionVector'
where vector.search(DescriptionVector, $query, 0.75)
order by score() desc
limit 10
```

Static indexes also let you mix vector search with structured filters in the same query:

```rql
from index 'Products/ByDescriptionVector'
where vector.search(DescriptionVector, $query, 0.8)
and Category = "Electronics"
and Price between 50 and 500
order by score() desc
```

That last one is the killer feature for real applications — semantic relevance *combined* with hard filters, in a single query, against a single system.

---

## Using It From Python

The RavenDB Python client exposes raw RQL queries through `session.advanced.raw_query()`. Combining that with `vector.search()` looks like this ([full source on GitHub](https://github.com/rusiqe/ravendb-devrel-portfolio/blob/main/04-demo/search.py)):

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

No embedding library. No separate vector client. Just an RQL query with a parameterised `vector.search()` call — the same session interface you'd use for any other RavenDB query.

Adding a category filter is one line ([search.py#L49–55](https://github.com/rusiqe/ravendb-devrel-portfolio/blob/main/04-demo/search.py#L49)):

```python
        """
        from Products
        where vector.search(Description, $query)
        and Category = $category
        order by score() desc
        limit $limit
        """
```

The structured filter and the vector search execute together inside RavenDB — there's no post-filtering step on the client.

Getting your data in is equally straightforward. RavenDB's bulk insert API handles everything; embeddings are generated automatically when queries arrive ([seed.py on GitHub](https://github.com/rusiqe/ravendb-devrel-portfolio/blob/main/04-demo/seed.py)):

```python
with store.bulk_insert() as bulk:
    for product in products:
        bulk.store_as(product, product.id)
```

No schema changes. No embedding pre-computation step. Store your documents as you normally would and let RavenDB handle the vector layer.

---

## Embedding Providers and the Built-In Model

When defining a static index, you have full control over how embeddings get generated. RavenDB integrates directly with:

- **OpenAI** (text-embedding-3-small, text-embedding-3-large, etc.)
- **Azure OpenAI**
- **Hugging Face**
- **Google AI**
- **Ollama** (for local models)
- **Mistral**

You configure the provider once on the index, and RavenDB handles the rest — including keeping embeddings up to date as your documents change.

But the option I find most interesting? **Zero external dependencies.**

RavenDB ships with `bge-micro-v2` built in. It's a compact, capable embedding model that runs entirely inside the database process. No API key. No network call. No rate limits. If you want to get started with semantic search today, you can do it without signing up for anything.

For many use cases — internal search, smaller datasets, privacy-sensitive applications — it's all you need.

---

## Why This Actually Matters

The standard approach to adding vector search to your stack goes something like this: spin up a separate vector database, write a pipeline to sync your data into it, figure out how to keep them consistent, and then manage two systems in production forever.

That's a real cost. Operational complexity isn't free.

RavenDB's approach is different. Your operational database *is* your vector store. Same system. Same data. Same query interface. When a document updates, the vector index updates. You're not running two separate systems with a sync job in between — you're running one.

This matters most when you're building things like:

- **Search engines** — semantic relevance over your own content
- **Recommendation systems** — find items similar to what a user has already engaged with
- **RAG pipelines** — retrieve the right context chunks before sending them to an LLM

In all of these, you want your AI-powered retrieval layer right next to your data. Not three hops away.

---

## Seeing It in Practice

To make this concrete, I built a [small demo](https://github.com/rusiqe/ravendb-devrel-portfolio/tree/main/04-demo): a 50-product catalog seeded into RavenDB, searchable via a Python CLI using `vector.search()` with the built-in bge-micro-v2 model.

The most interesting part of building it was watching what keyword search would have missed. These queries contain *no shared words* with the products they return:

| Query | Keyword result | Semantic result (RavenDB) |
|---|---|---|
| "something warm for winter travel" | 0 results | Canada Goose Expedition Parka |
| "relieve back pain at my desk" | 0 results | Lumbar Support Pillow, Monitor Arm |
| "drink coffee without electricity" | 0 results | Bodum Chambord French Press |
| "peripheral for heavy typists" | 0 results | Keychron K2 Mechanical Keyboard |
| "muscle recovery after a run" | 0 results | TriggerPoint Foam Roller |
| "books for becoming a better programmer" | 0 results | Clean Code, Designing Data-Intensive Apps |

Every one of these is a query that a real user would type. None of them would return a single result from a keyword-based system. All of them work with `vector.search()` on a plain text description field, with zero configuration beyond installing RavenDB.

The demo also shows the combined filter in action — `vector.search(Description, "muscle recovery after a run") and Category = "Fitness"` — which is where you'd use this in a real application: semantic relevance scoped to a category, price range, brand, or any other structured attribute. One query. One system.

You can clone the demo and have it running in under five minutes: [github.com/rusiqe/ravendb-devrel-portfolio/tree/main/04-demo](https://github.com/rusiqe/ravendb-devrel-portfolio/tree/main/04-demo).

---

## Try It

If you're already running RavenDB 7.0, you can start with a dynamic query right now — no configuration required. If you want to go further, the [RavenDB documentation on vector search](https://ravendb.net/docs) walks through defining static indexes and configuring embedding providers.

For a working example with Python client code you can run locally, the [demo project](https://github.com/rusiqe/ravendb-devrel-portfolio/tree/main/04-demo) has everything: seed script, search CLI, and 50 products chosen specifically to show where semantic search beats keyword search.

The infrastructure problem is already solved. What are you going to build with it?

---

*Taurai is a technical writer and DevRel engineer. Find more at [taurai.eu](https://www.taurai.eu)*

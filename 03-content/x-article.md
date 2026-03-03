# Most Databases Are Searching Wrong. Here's What That Actually Means.

Your database finds documents by matching words. That's it. Search for "fast" and you get back anything containing the string "fast." Search for "high-performance" and get nothing — even though that's the same idea.

This isn't a bug. It's just how keyword search works. The problem is that keyword search is the default for almost everything, and most developers never question it.

Semantic search does something fundamentally different: it searches on *meaning*.

## The Concept Takes 60 Seconds

An embedding is a way of converting text into a list of numbers. Those numbers encode what the text *means*, not how it's spelled. Two sentences that mean similar things produce similar numbers. Two sentences that mean different things produce numbers that are far apart.

So instead of matching characters, you're measuring distance in meaning-space. Your query becomes a point. Your documents become points. Search means finding the nearest neighbors.

That's it. That's the whole idea.

## Why RavenDB's Approach Is Different

Most people who add vector search to their stack end up with two systems: their main database, and a separate vector store. Then a sync job to connect them. Then the fun of keeping them consistent in production.

RavenDB 7.0 skips all of that. Vector search is built directly into the database — not as a plugin, not as an add-on. It uses an HNSW graph (one of the best nearest-neighbor algorithms available) powered by its Corax index engine, and it's fully integrated with RQL, RavenDB's query language.

Same database. Same data. Same query interface.

## Two Ways to Use It

Dynamic queries let you drop vector search into any query without defining anything upfront. Great for prototyping. You write a query, RavenDB auto-generates the index.

Static indexes give you full control. You define the vector field, configure the HNSW parameters, and — critically — you can mix semantic search with regular structured filters in the same query. Semantic relevance *plus* "price between 50 and 500" *plus* "category equals Electronics." One query. One system.

## You Don't Even Need an API Key

RavenDB ships with a built-in embedding model called bge-micro-v2. It runs entirely inside the database process. Zero external dependencies. No OpenAI key, no network call, no rate limits.

If you want to use OpenAI, Azure, Hugging Face, Google AI, Ollama, or Mistral instead — all supported. But you don't have to.

## The Actual Point

The value of having vector search inside your operational database isn't just convenience. It's consistency. When a document updates, the vector index updates. You're not managing a sync pipeline between two systems. You're just running your database.

For search engines, recommendation systems, and RAG pipelines — where you need your retrieval layer close to your data — this is a meaningful architectural difference.

If you're already on RavenDB 7.0, you can try a dynamic vector query right now. No setup required.

---

More on this at [taurai.eu](https://www.taurai.eu) — follow along for more technical writing on databases, developer tools, and the infrastructure behind AI applications.

# Teleprompter Script — Semantic & Vector Search in RavenDB
**Target duration:** 3:30 – 4:00
**Reading pace:** ~130 wpm
**Word count:** ~470
**Format:** Each line is one breath. Blank lines = deliberate pause.

---
> 💡 **Before you hit record:** Slow down on HNSW and bge-micro-v2.
> Spell out "B-G-E micro version 2" the first time if your audience is non-technical.

---

Most developers add vector search as an afterthought.

Pinecone here, Weaviate there,
a sync job holding it all together.

It works. Until it doesn't.

---

When you search a traditional database, you're matching characters.

You search for the word *fast* —
and you get back documents that contain the word *fast.*

That's the whole trick.

It breaks down fast though.

*High performance.* *Low latency.* *Quick processing.*

Those all mean the same thing.
But keyword search has no idea.

It's not stupid. It's just working at the wrong level.

---

That's where **semantic search** comes in.

Semantic search works on *meaning*, not words.

The mechanism behind it is something called an **embedding.**

An embedding converts text into a list of numbers —
a vector — that encodes what the text *means.*

Feed "fast car" and "high-speed vehicle" into a good embedding model
and you get two vectors that sit close together.

Feed in "fast car" and "tax policy"
and those vectors will be far apart.

That distance becomes your search signal.

Instead of matching words,
you're finding *meaning.*

---

Now here's where **RavenDB** comes in.

Starting with version 7.0,
vector search is built directly into the database.

Not a plugin. Not a sidecar.
Part of the core indexing engine.

Under the hood, RavenDB uses **Corax** to build an **HNSW graph —**
Hierarchical Navigable Small World —
one of the best algorithms for approximate nearest-neighbor search at scale.

You get vector search right where your data already lives.

No sync jobs. No separate system. No consistency problems.

---

There are two ways to use it.

**Dynamic queries** — write a query,
and RavenDB creates the index automatically.
Great for prototyping.

**Static indexes** — define the vector field explicitly
and get predictable, production-ready performance.

Static indexes also let you combine vector search with regular filters
in a single query.

Semantic relevance, a category filter, and a price range —
all in one round trip.
That's the one that matters in real applications.

---

For embeddings, you can connect RavenDB to
OpenAI, Azure, Hugging Face, Ollama, Google AI, or Mistral.

Or — and this is the part I find most interesting —
you can use the **built-in model.**

RavenDB ships with **bge-micro-v2** baked in.

It runs inside the database process.
No API key. No network call. No rate limits.

You can start using semantic search today,
without signing up for anything.

---

I built a small demo to make this concrete.

Fifty products, seeded into RavenDB,
searchable from the command line.

The queries that stayed with me
were the ones with *zero* shared words with their results.

*"Drink coffee without electricity"* — returns the French press.

*"Peripheral for heavy typists"* — returns the mechanical keyboard.

*"Relieve back pain at my desk"* — returns the lumbar support pillow.

None of those queries share a word with the product description.

Keyword search returns nothing.
RavenDB returns exactly what you were looking for.

---

That's the gap.

And your database can already close it.

If you're on RavenDB 7.0,
you can start with a dynamic query right now —
no configuration required.

The demo project and the full walkthrough
are linked in the description.

Thanks for watching.

---

## Emphasis guide
| Word / phrase | How to say it |
|---|---|
| **semantic** | Stress the *se-MAN-tic* — it's the point of the whole video |
| **meaning** | Slow down. Let it land. |
| **HNSW** | "H-N-S-W" — spell it out, don't try to say it as a word |
| **Corax** | "KOR-ax" |
| **bge-micro-v2** | "B-G-E micro version 2" |
| **Zero shared words** | Pause before and after this phrase |

## Slide / demo cues
- **[0:00]** Start on your intro frame or a blank screen
- **[~1:00]** Switch to a diagram of keyword vs semantic if you have one
- **[~2:00]** Show the RavenDB docs page or the Studio
- **[~2:45]** Switch to terminal — run the demo live
- **[~3:15]** Show the comparison table from the blog post
- **[~3:30]** End on your face / outro frame

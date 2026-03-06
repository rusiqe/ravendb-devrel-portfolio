# Video Script — Semantic Search in RavenDB
**Format:** Talking head → screen share (code) → live terminal demo
**Target duration:** 5–7 minutes
**After-read:** Link to `03-content/blog-post.md` in description

---
> 🎬 **Setup checklist before recording:**
> - RavenDB Cloud cluster running, products seeded (`python seed.py`)
> - `search.py` tested — confirm at least 3 demo queries return results
> - Editor open to `search.py` at the `SEMANTIC_QUERY` block (line 42)
> - Terminal ready in the `04-demo/` directory
> - Second terminal tab open with `search.py` ready to run interactively

---

## PART 1 — HOOK
**[ON CAMERA]**

Most search is broken.

Not because it's buggy.
Because it's doing the wrong thing.

When you type a query into a keyword-based search engine,
it looks for documents that contain those exact words.

Search for *"fast"* — you get documents with the word "fast."

That's it. That's the whole trick.

So when a user types *"something warm for winter travel,"*
and your product is described as an *"Arctic-rated insulated down parka"* —
keyword search returns nothing.

The user leaves.

Semantic search fixes this.
And as of RavenDB 7.0, you don't need a separate system to do it.

---

## PART 2 — THE CONCEPT
**[ON CAMERA — optionally cut to a simple diagram]**

Here's the idea in 30 seconds.

Semantic search works on *meaning*, not words.

An **embedding** is a way of converting text into a list of numbers — a vector —
that encodes what the text *means.*

Two pieces of text that mean similar things
produce vectors that are close together.
Two pieces of text that mean different things
produce vectors that are far apart.

*[gesture or diagram: two dots close together, two dots far apart]*

Instead of matching words, you're measuring distance.
The closest results are the most semantically similar.

RavenDB builds an index of those vectors —
using an algorithm called **HNSW** under its **Corax** indexing engine.
It scales to millions of documents and updates incrementally as data changes.

---

## PART 3 — THE CODE
**[SWITCH TO EDITOR — open `04-demo/search.py`, scroll to line 42]**

Let me show you how little code this actually takes.

**[HIGHLIGHT lines 42–47: `SEMANTIC_QUERY`]**

This is the entire search query.

```python
from Products
where vector.search(Description, $query)
order by score() desc
limit $limit
```

`vector.search` takes two arguments —
the field to search on, and the query string.

RavenDB handles the embedding generation using its built-in **bge-micro-v2** model.
That's running inside the database process.
No API key. No external service. Nothing to configure.

The results come back ordered by similarity score.

**[SCROLL DOWN to lines 49–55: `SEMANTIC_QUERY_WITH_CATEGORY`]**

This is the version with a category filter.

```python
from Products
where vector.search(Description, $query)
and Category = $category
order by score() desc
limit $limit
```

One extra `and` clause.

That's the part that's hard to do with a standalone vector store —
combining semantic search with a structured filter
in a single query, against a single system.

**[SCROLL DOWN to lines 72–81: `run_search()`]**

And here's how it's executed.

Standard RavenDB session, `raw_query`, add your parameters, return results.

No vector library. No embedding client.
The same session interface you'd use for any other RavenDB query.

**[BRIEFLY SHOW `seed.py` lines 49–58]**

The data gets in via a bulk insert —
no schema changes, no pre-computation step.
Store your documents exactly as you normally would.
RavenDB builds the vector index from there.

---

## PART 4 — LIVE DEMO
**[SWITCH TO TERMINAL — `cd 04-demo/`]**

Let me show you what this does with real queries.

**[RUN: `python search.py`]**

> *Wait for the prompt to appear*

I'm going to start with queries that share **zero words** with any product in the catalog.
That's the test that keyword search fails completely.

---

**[TYPE: `drink coffee without electricity`]**

> *Let results render, pause for viewer to read*

The French press. Described as "produces a rich, full-bodied brew in four minutes — no paper filters, no electricity, no pods."

Not a single word in common with the query. RavenDB found it anyway.

---

**[TYPE: `peripheral for heavy typists`]**

> *Pause*

Keychron K2 Mechanical Keyboard. "Ideal for developers and writers who spend hours typing."

Again — *"peripheral"* and *"heavy typists"* appear nowhere in that description.

---

**[TYPE: `something warm for winter travel`]**

> *Pause*

Canada Goose Expedition Parka. "Arctic-rated insulated down parka certified for temperatures as low as -30°C."

---

**[TYPE: `q` to exit, then RUN: `python search.py "muscle recovery after a run" --category Fitness`]**

Now the same idea with a category filter.

We're asking for muscle recovery help — filtered to Fitness products only.

> *Pause on results*

TriggerPoint Foam Roller and the resistance bands.

Semantic relevance scoped to a category. One query. One system.

---

## PART 5 — OUTRO
**[BACK ON CAMERA]**

That's semantic search in RavenDB —
built into the database, zero extra infrastructure,
and working in Python with about 15 lines of code.

I've written a full breakdown of how the indexing works,
how static indexes give you more control,
and the full list of embedding providers you can connect —
link to the article is in the description.

The demo project is open source —
linked there too if you want to clone it and run it yourself.

---

## Screen cue summary
| Time | Screen |
|---|---|
| 0:00 – 1:00 | Face / talking head |
| 1:00 – 1:30 | Optional: simple vector space diagram |
| 1:30 – 3:00 | Editor — `search.py` lines 42–81, then `seed.py` lines 49–58 |
| 3:00 – 5:30 | Terminal — interactive demo |
| 5:30 – 6:00 | Face / talking head for outro |

## Demo query order
1. `drink coffee without electricity` — no shared words, obvious result
2. `peripheral for heavy typists` — slightly more abstract
3. `something warm for winter travel` — the most dramatic gap
4. `python search.py "muscle recovery after a run" --category Fitness` — show the filter

## If you fumble a query
Just say *"let me try that again"* and retype. Keeps it real.
Don't cut around it — authenticity plays better than polish for DevRel content.

# Teleprompter Script — Map/Reduce in RavenDB
**Target duration:** 5:30 – 6:30
**Reading pace:** ~130 wpm
**Word count:** ~740
**Format:** Each line is one breath. Blank lines = deliberate pause. [ADVANCE] = click to next slide.

---
> 💡 **Before you hit record:**
> Run through slides 5–7 once before recording — the code examples need a beat to land.
> You don't need to read the code out loud. Just reference it and let the viewer read.

---

## [SLIDE 1 — TITLE]

This is a deep dive into Map/Reduce in RavenDB.

How aggregation works,
why it's different from what you're used to,
and why it changes the way you think about read performance.

Let's get into it.

---

## [SLIDE 2 — THE PROBLEM]

[ADVANCE]

Aggregation is expensive.

In a traditional database, every time you ask for a count,
a sum, or a group-by —
the database scans the collection, does the math, and returns the result.

Do that once? Fine.

Do it on every page load, for a million users?
Now you have a problem.

The usual fix is background jobs and caching.
Which works — until your cache is stale,
or your job falls behind,
or both happen at once.

There's a better model.

What if aggregation happened *incrementally* — as data changes —
not all at once when you query?

You'd pay a small cost on every write.
Reads would be instant, no matter how much data you have.

That's exactly what Map/Reduce indexes do.

---

## [SLIDE 3 — CONCEPT]

[ADVANCE]

Map/Reduce is a simple idea.

Imagine a warehouse counting inventory.

Instead of one person counting everything at the end of the day,
every worker *maps* their section —
"I have 5 red boxes" —
and a supervisor *reduces* all those reports into a total.

Change one box? Only that section re-reports.

That's the pattern.

**Map** — run a function over each document.
Emit key-value pairs.

**Reduce** — group by key.
Aggregate into a final value per group.

**Query** — hit pre-computed results.
Zero aggregation cost, every single time.

---

## [SLIDE 4 — ARCHITECTURE]

[ADVANCE]

Now, you might have heard of MapReduce from Hadoop.
That's a different thing.

Hadoop-style MapReduce distributes work across a cluster.
It runs in batches, periodically.
By the time you query, the results could be hours old.

It's designed for petabyte-scale ETL. Not for live queries.

RavenDB's Map/Reduce runs on each node independently.
Triggered incrementally, on every write.
Results are always current.

Here's how I think about it:

RavenDB breaks computation across *time*, not across machines.

Every write does a little work
so every read costs nothing.

---

## [SLIDE 5 — BASIC CODE]

[ADVANCE]

Here's a basic Map/Reduce index in C#.

We're counting products per category.

The **Map** function runs once per document —
it emits the category name and a count of one.

The **Reduce** function groups those results by category
and sums the counts.

RavenDB runs this incrementally as documents change.
Add a product — one emit, one re-reduce for that category.
The index stays current.

Now click the **RQL tab.**

That's the query.
Two lines.
From the index, order by count.

No scan. No group-by at query time.
Just reading pre-computed results.

---

## [SLIDE 6 — MULTI-MAP]

[ADVANCE]

Multi-Map takes this further.

With a Multi-Map index,
you can aggregate across multiple collections in a single index.

This example pulls from Employees, Companies, and Suppliers —
three separate collections —
and reduces them into one result per city.

One query. One result per city. Combined view.

No joins. No cross-collection scans.

Switch to the **RQL tab.**

You're querying Cities/Details
like it's a single flat collection.
The complexity is invisible at query time.

---

## [SLIDE 7 — OUTPUT REDUCE TO COLLECTION]

[ADVANCE]

This is one of my favourite RavenDB features.

Normally, a Map/Reduce index keeps its results inside the index.

**OutputReduceToCollection** writes those results
as *real documents* into a named collection.

In this example, we're generating daily sales summaries —
one document per day, automatically maintained.

Because they're real documents,
you can do anything with them.

Chain another index on top for monthly roll-ups, then yearly.
Subscribe to them with data subscriptions.
Push them to external systems via ETL.
Or just query them directly.

Flip to the **RQL tab** to see the query.

Notice you can also load a single day by its predictable document ID —
*sales/daily/* followed by the date.

That pattern is incredibly useful for time-series dashboards.

---

## [SLIDE 8 — USE CASES]

[ADVANCE]

Map/Reduce shows up everywhere once you know it's there.

Dashboards and analytics — always pre-computed, always fast.

Inventory and catalog — consistent counts across millions of SKUs.

Time-series roll-ups — daily into monthly into yearly, chained automatically.

Cross-collection stats — Multi-Map across your entire data model.

Order intelligence — revenue per product, frequency per customer,
without a single expensive GROUP BY scan.

And event sourcing —
live read-model projections, no separate projections service required.

---

## [SLIDE 9 — SUMMARY]

[ADVANCE]

The key difference is this.

Traditional databases do expensive aggregation *when you query.*

RavenDB does it incrementally *when you write.*

Results are always current.
Zero aggregation cost at query time.
No extra infrastructure.

That's Map/Reduce in RavenDB.

Thanks for watching.

---

## Emphasis guide
| Word / phrase | How to say it |
|---|---|
| **incrementally** | Stress this — it's the core concept |
| **Map** / **Reduce** | Say these like they're proper nouns — they are |
| **time, not machines** | Slow down. This is the memorable line. |
| **OutputReduceToCollection** | "Output-Reduce-To-Collection" — say each word clearly |
| **pre-computed** | Stress the *pre* — it's the whole point |

## Timing guide (per slide)
| Slide | Target time |
|---|---|
| 1 — Title | 0:15 |
| 2 — Problem | 1:00 |
| 3 — Concept | 1:00 |
| 4 — Architecture | 0:55 |
| 5 — Basic code | 0:55 |
| 6 — Multi-Map | 0:50 |
| 7 — OutputReduceToCollection | 1:00 |
| 8 — Use cases | 0:45 |
| 9 — Summary | 0:30 |
| **Total** | **~7:10** |

> Trim if needed: Slides 7 and 8 have the most room to cut.
> Slide 4 (architecture comparison) is the most important — don't rush it.

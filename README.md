# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This is a question-answering system built over the `city_guides` corpus:
fourteen travel guides to a set of invented towns, Brightwater, Halden Bay,
Kestrelford, Thornby Wells, Corry Vale and the rest, plus cross-cutting guides
on eating, walking, seasons, regional transport and accessibility. Ask it a
question and it retrieves the passages most likely to hold the answer, then has
a model write the answer from only those passages and name the file it came
from.

The questions it's built to handle are the practical, specific kind a traveller
would actually ask: comparisons between towns ("What's the difference between
Kestrelford's pubs and Marchwood's kitchens in terms of when you can eat?"),
what's available at a given time of year ("What can you do at Givens Mill in
spring or summer that you can't do in winter?"), and small comparisons of time
or cost ("How much extra time should you allow to reach the Elder Ness
lighthouse at the highest spring tides, and why?"). Each one has a right answer
sitting in the guides, which is what makes it checkable. Questions the guides
don't cover, like the capital of Mongolia or how to write a Rust for loop, get
refused rather than guessed at, since a relevance cutoff stops them before they
ever reach the model.

## Chunking Strategy

**Chunk size:** 600
**Overlap:** 100


My split_documents function chunks by paragraph first and only drops into the fixed-size sliding window when a single paragraph is longer than CHUNK_SIZE. So for this corpus, CHUNK_SIZE and CHUNK_OVERLAP aren't really what's driving the chunk boundaries, paragraph structure is.

When I went through the travel_guides corpus, almost no paragraph comes close to 600 characters, most are much shorter than that. That matters for what these two settings are actually doing here. If I lowered CHUNK_SIZE further, it wouldn't make my chunks more precise, it would just force the sliding-window fallback to kick in on paragraphs that currently pass through fine, cutting whole thoughts in half just because they hit an arbitrary limit. A short paragraph is usually one complete idea, so splitting it doesn't add precision, it just breaks it: both halves lose context, and neither one is enough on its own to answer a question.

That's why I kept CHUNK_SIZE at 600, it stays comfortably above the length of my most characters paragraph, so almost every paragraph ends up as its own clean, unsplit chunk. CHUNK_OVERLAP at 100 is only there for the rare case: a longer paragraph, or a few short ones merged together by merge_short_paragraphs, that ends up over 600 characters and has to go through the sliding-window path. In that case, 100 characters of overlap is enough to keep a sentence from getting cut cleanly at a chunk boundary, without duplicating a lot of text the way a bigger overlap like 250 would, especially since this fallback path barely gets used anyway.

So overall, for this corpus, paragraph structure is what actually sets my chunk boundaries. CHUNK_SIZE and CHUNK_OVERLAP are just tuned as a backup for the few paragraphs long enough to need the fallback, not as the main way I'm splitting.


<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

## Sample Chunks

From `python app.py chunks -n 5` — 115 chunks total, five spread across the corpus.

**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

**Chunk 2** — source: `guide_corry_vale.md#4` — produced by: `chunker.py::split_documents`

```
## What to see

The valley itself is the attraction. The footpath network is dense and well marked, and a circuit taking in three of the four villages is about nine miles with 500 metres of ascent. The chapel in the second village is 12th century and always unlocked.
```

**Chunk 3** — source: `guide_givens_mill.md#4` — produced by: `chunker.py::split_documents`

```
## What to see

The mill runs tours on the hour from 11 to 3 and the machinery is operating during them, which is loud and much more impressive than a static exhibit. The church has a Saxon doorway. The river walk downstream reaches Brightwater in about three hours.
```

**Chunk 4** — source: `guide_marchwood.md#3` — produced by: `chunker.py::split_documents`

```
## Eat and drink

The best eating is in the Northgate district, a 12-minute tram ride from the station, where about thirty restaurants sit within four streets. The area immediately around the station is uniformly poor and expensive. Marchwood keeps later hours than anywhere else in the region — kitchens serve until 10:30pm, and until midnight on Fridays and Saturdays.
```

**Chunk 5** — source: `guide_seasons.md#2` — produced by: `chunker.py::split_documents`

```
## Summer, June to August

June is excellent everywhere. July and August split: Halden Bay becomes very
busy and the parking problem dominates, Kestrelford fills with walkers, and
Brightwater goes quiet to the point of dullness with the university empty.
```

**What these five show:** all five carry their own heading, so every chunk says
what it is about before it says anything else — `## Eat and drink` together with
Marchwood's kitchen hours, not one without the other. Each one could answer a
question on its own, which is the test the `chunks` command asks you to apply.

It took two tries to get here. My first version split on blank lines and nothing
else, and because a Markdown heading sits between two blank lines, every `##` in
the corpus came out as its own chunk — 213 chunks, of which a good fraction read
`## Where to stay` and stopped there. Useless on its own, and worse, it stripped
the heading off the section below it, so neither piece knew what it was about.
Merging any paragraph under 50 characters into the one after it fixed both halves
of that problem and brought the corpus down to 115 chunks.

The whole corpus now comes out at 250 characters per chunk on average, shortest
71 and longest 509. That longest chunk is the number that matters: it is under
`CHUNK_SIZE = 600`, so the fixed-size sliding window never runs on this corpus at
all. Every one of the 115 chunks is a whole paragraph or a small group of them,
and nothing is cut mid-sentence.

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** What's the difference between Kestrelford's pubs and Marchwood's kitchens in terms of when you can eat?

**Answer:** Kestrelford's pubs only serve food during specific windows (12 to 2 and 6 to 8:30) with nowhere to eat outside of those times, whereas Marchwood keeps later hours with kitchens serving until 10:30pm, and until midnight on Fridays and Saturdays. 

Sources: `guide_eating.md`, `guide_marchwood.md`, and `guide_kestrelford.md`.

Sources retrieved: guide_eating.md, guide_kestrelford.md, guide_marchwood.md


**My relevance cutoff:** `THRESHOLD = 0.6` in `config.py`.

I ran all ten questions through retrieval and wrote down the best (lowest)
distance for each. The two groups didn't overlap at all. Everything my guides
cover landed between **0.2132 and 0.4247**, and everything they don't landed
between **0.8026 and 0.9747**. That's a gap of **0.378** with nothing inside it,
which is wider than the spread of either group on its own.

The midpoint of the gap is 0.6136, so the starter's default of 0.6 was already
almost exactly where I would have put it. I left it alone instead of changing
the number just to show I did something. It clears my worst in-corpus question
by 0.175 and my closest out-of-scope question by 0.203, so there's room on both
sides and no single question is deciding where the cutoff falls.

The honest caveat is that a gap this clean says as much about my out-of-scope
questions as it does about my cutoff. Diesel engines and the 1994 World Cup are
nowhere near a set of regional travel guides, so they were never a hard test to
begin with. A question like "what's the best restaurant in Edinburgh?" is the
right topic but the wrong region, and it would probably land much closer to the
boundary. I don't actually know from this data which side of 0.6 it would fall
on.

| Question | In corpus? | Best distance |
|---|---|---|
| What's the difference between Kestrelford's pubs and Marchwood's kitchens in terms of when you can eat? | yes | 0.3660 |
| What's the most common source of confusion for visitors using buses in the region? | yes | 0.4247 |
| What can you do at Givens Mill in spring or summer that you can't do in winter? | yes | 0.3846 |
| How much extra time should you allow to reach the Elder Ness lighthouse at the highest spring tides, and why? | yes | 0.2132 |
| How much cheaper is Fell Street compared to the Halden Bay harbour front, and why is it cheaper? | yes | 0.4007 |
| What is the capital of Mongolia? | no | 0.8026 |
| How do I change the oil in a diesel engine? | no | 0.8917 |
| Who won the 1994 World Cup? | no | 0.9747 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.8486 |
| How do I write a for loop in Rust? | no | 0.8130 |

Worst in corpus 0.4247 → best out of scope 0.8026. Cutoff 0.6 sits in the gap.

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** First, I asked Claude to write the chunking function based on my strategy. After it gave me the function, I ran a test to look at the chunks and noticed it was treating each header as its own complete paragraph, which I didn't want. So I went back and prompted Claude again to fix that, so headers get attached to the paragraph that follows them instead of standing alone.

**2.** I also asked Claude to help me explore my corpus (where are the travel guides for?), also mostly around character counts, things like the longest and shortest paragraph length, and the longest header title.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

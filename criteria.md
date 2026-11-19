# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 3 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->
Most of my questions is kinda specific, and mostly have only three documents or less mention it, so I expect a 50/50


---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->
I set this at 5 of 5 because citing a source doesn't depend on retrieval being correct, the source filename gets attached to every chunk automatically, so it should show up every time, even on the answers that get the content wrong.
---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate stops it and the system returns "I don't have enough information about that" — in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->
I don't have my distances yet since this is written before Milestone 4, but out-of-scope questions should be obviously unrelated to a set of regional travel guides, so I expect the gate to catch most of them without much trouble.

---

## 4. Something about your chunks
At least 4 of 5 sampled chunks are over 71 characters long and end on a completed sentence, with no thought cut off mid-way at either boundary.

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->



**Why this target:**
I picked 71 because that's the length of the shortest real paragraph in my corpus, "The Kestrelford Saturday market builds back to full size through April." (guide_seasons.md)

---

## 5. Your choice
For questions requiring a number from the text (opening hours, prices, distances), the retrieved chunk contains the exact number needed, in at least 1 of 2 such test questions.

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->



**Why this target:**
I set this at 1 of 2 because only 2 of my 5 questions ask for a number, and I haven't tested this yet. With such a small sample, one miss shouldn't fail the whole criterion, but two would suggest a real problem


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->

# Capstone

Five criteria for the hosted, instrumented version on Render, written before
any trial runs. Each trial is one run of `tools/send_questions.py` against the
Render URL: 5 in-corpus questions, 5 out-of-scope questions and 5 bad inputs.

---

## 1. Every request leaves a complete log record

In every trial, all 15 requests to `/ask` leave exactly one log record in
Render's logs, with every field filled in (`status`, `duration_ms`, both token
counts, and `error` when something went wrong). 15 of 15.

**Why this target:**
The log is the whole point of this capstone. If even one request goes missing,
especially a failed one, then I can't trust the cost or the timing numbers
I work out from it, so anything under 15 of 15 is a miss.

---

## 2. Bad input gets a 400, not a 500

Every bad request (an empty question, a missing `question` key, a body that
isn't JSON, a question that isn't a string, a JSON list instead of an object)
gets a 400 with a message saying what to send, not a 500. 5 of 5.

**Why this target:**
All five of these are the caller's mistake, not the server's, so all five
should be a 400. One crash already showed up in Render's logs as a full
traceback while I was testing the logging, so this is the bad path I most expect to fail.

---

## 3. Warm answers come back in under 5 seconds

For answered questions after the first one in a trial, at least 9 of 10 have a
`duration_ms` under 5000 in the log. Each trial has 5 answered questions, so
this is counted over the first two trials combined.

**Why this target:**
In my first test on Render, warm answers took between 3.8 and 4.7 seconds,
and almost all of that was embedding and search, not the model. 5 seconds
is only just above that, so a slow day on Render's shared CPU could
push me over it. I'm allowing one miss out of 10 so a single slow request
doesn't decide it.

> **Revised in capstone, after the before trials:** For answered questions
> after the first one in each trial, at least 11 of 12 across all three trials
> have a `duration_ms` under 5000 in the log.
>
> **Why revised:** The original couldn't be counted the way I wrote it. Each
> trial has 5 answered questions, so "after the first one" leaves 4 per trial,
> and two trials only give 8, not 10. Using all three trials gives 12. 11 of 12
> is the closest whole number to the 9 of 10 (90%) I meant, so the target
> doesn't get any easier. 10 of 12 would have been lowering it. The 5-second
> line stays the same.

---

## 4. A cold start still answers

After the service has been asleep for at least 15 minutes, the first `/ask`
still returns a 200 with an answer within 90 seconds on the client's clock,
not a timeout or a 502. 3 of 3 times.

**Why this target:**
The first request after my deploy took 26.3 seconds just inside the app,
loading the embedding model. A wake from sleep adds Render's own spin-up on top
of that. 90 seconds leaves room for both but stays under gunicorn's 120-second
timeout. Someone who waits that long and then gets an error is the worst
result this system can give.

---

## 5. The hosted gate still refuses out-of-scope questions

On Render, all 5 out-of-scope questions in `questions.py` are refused with 0
tokens used, in every trial. 5 of 5.

**Why this target:**
In Unit 2 the gate refused 5 of 5 locally, and the out-of-scope distances
(0.80 to 0.97) were nowhere near the 0.6 cutoff. Hosting shouldn't change any
of that, since the index and the embedding model are the same, so any miss
would mean the hosted version isn't the same system. 0 tokens also proves
the refusal happened before the model was called, which matters for the
cost numbers.

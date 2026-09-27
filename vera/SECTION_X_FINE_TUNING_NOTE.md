# Section X — Fine-tuning note (discussion only, no build)

**SYNTHETIC / FOR TRAINING ONLY.** Meridian Industries, Vera, and every figure referenced here are fictional.

## What RAG already solved for Vera

Everything built in Parts 2–4 of this lab solved the "get the right numbers"
problem: retrieval + citation + refusal/escalation guarantees that every
figure Vera states traces back to a real, closed-period Meridian document
(see `vera/evals.py` — 16/16 golden cases, including zero hallucinated
numbers and zero missing citations across the run).

RAG does **not** solve a different, separate problem: **consistent voice at
scale**. `board_narrative_style_guide.md` lays out six rules a CFO wants
every variance commentary to follow — lead with the number, name the
driver, no hedging, no forward guidance, always cite, stay under three
sentences. Right now, `narrative_drafter()` (`vera/agents.py`) just echoes
retrieved passages verbatim — it doesn't attempt to write in that voice at
all. If Meridian's Controller needed hundreds of these commentary lines a
year, all matching the CFO's exact tone, that's the kind of scale problem
fine-tuning is suited for and pure prompting tends to drift on.

## Why we didn't reach for it in this lab

Section B's decision framework: escalate only as far as the requirement
demands.

- A well-instructed model with the style guide in its context window gets
  most of the way to consistent tone on a *handful* of examples — that's
  prompting, and it's cheap to iterate on.
- Fine-tuning only earns its cost once you have (a) a labeled set of
  CFO-approved commentary examples to train on, and (b) a *measured*,
  *specific* gap that prompting-with-style-guide couldn't close — not a
  hunch that it might drift eventually.
- Vera's build in this lab never got past a handful of test questions
  (the 16-case golden set), so there's no evidence yet of a drift problem
  fine-tuning would actually fix. Reaching for it now would be solving a
  problem we haven't observed.

## The concrete trigger, if it ever comes

If Vera moves from a prototype to something the Controller's team uses to
draft hundreds of real board commentary lines a year, the right sequence
is:

1. Give `narrative_drafter()` a real model call with
   `board_narrative_style_guide.md` in context (still prompting, not
   fine-tuning) and measure tone consistency against a CFO-reviewed sample.
2. If that measured gap is real and doesn't close with better prompting,
   collect the CFO-approved commentary examples needed as training data.
3. Fine-tune *only* the Narrative Drafter role's model — never the FP&A
   Analyst (which does retrieval, not writing) and never on top of RAG's
   job of sourcing the numbers. RAG still owns "which figure is correct";
   fine-tuning would only ever own "how it's phrased."

No code changes accompany this note — per the booklet, Section X is a
design discussion, not a build step.

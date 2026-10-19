# AI reviewer

`python -m applied_econometrics.review` reads the *Result* section of each paper README and the paper's tables.

1. **Python** extracts every number from the LaTeX tables and stats files (~130–170 cells per paper, with captions)
   and splits the text into statements.
2. **The model** (Claude Haiku 5.5, structured JSON output validated by a JSON Schema) maps each number in a statement to
   a table cell and judges the reading: significance against the stars, sign, standard error vs coefficient, elasticity
   vs percentage points, IRR, causal wording on associational designs, "proves" from a non-rejection.
3. **Python** re-checks every mapped number against its cell, up to the rounding shown on each side. A number is never
   declared correct on the model's word; if the model points at a cell that does not hold the number, Python overrides it.

**Golden set** (`tests/golden/statements.json`): 30 statements, 18 with a planted error (wrong digit, wrong value, standard
error read as coefficient, significance claimed without stars, elasticity read as percentage points, IRR misread, causal
claim, "proves" from a non-rejection) and 12 correct. With the final prompt, three live runs caught 18, 17 and 18 of the
18 planted errors, with 0 false alarms on the 12 correct statements.

How it got there, measured on the golden set each time (`reports/experiments/`):

| Change | Planted errors caught | False alarms on the real write-ups |
|---|---|---|
| First version | 16–17 of 18 | 2–4 sentences |
| Low-effort thinking on | 16 | — (kept off: no gain) |
| Table captions in the facts, "consistent with" allowed | 16–17 | 2 |
| Reason before verdict in the JSON Schema | 15 | 0 |
| "A wrong value for a quantity a cell holds is a mismatch, not *not in tables*" | 17–18 | 0 |

Putting the reason before the verdict removed the false alarms whose own reason said "correct". The last rule fixed the
main miss: the model saw that "R² = 0.404" was wrong but filed it as *not in tables*, which left Python nothing to check.

**On the real write-ups**: 26 statements, 60 numbers, 59 matched to a cell and confirmed by Python (one is computed in
the text), 0 flags (`reports/review_*.md`).

**Cost and safety**: one full review is 7 calls, about 45k input tokens, **US$ 0.008**; the committee memo with its review,
about US$ 0.004. Hard cap of 20 calls per run, 60 s timeout, SDK retries for network errors, one retry when the answer fails the schema or the checker (e.g. a number
that is not in the statement), one JSON log line per call with tokens. Answers are recorded in `recordings/`: the same
request is never paid twice, and without a key the reviewer replays them (demo mode, used by the tests).
The key is read from `ANTHROPIC_API_KEY` or a local `.env` (see `.env.example`) and never printed or committed.

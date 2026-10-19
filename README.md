# Applied econometrics

Short empirical papers built the same way: Python pulls the data from public sources, automatic checks test the base
before any model runs, each specification step is justified by what the previous one showed, and an AI reviewer checks
every number and every coefficient reading in the write-up against the tables.

```
public APIs ──► raw data ──► data checks (JSON report) ──► model + refinement ──► tables ──► AI reviewer
 BCB, IBGE,                  FAIL stops the run             each step has a why              Python re-checks
 SINAN, CVM                                                                                  every number
```

## Papers

| # | Question | Data | Headline |
|---|---|---|---|
| [01](papers/01-phillips-curve/) | Is there a Phillips-curve trade-off in Brazil, 2012–2026? | BCB APIs: IPCA, PNAD unemployment, Focus expectations | No. Inflation follows inertia (0.398) and expectations (0.686); unemployment is flat; a vertical long-run curve is not rejected |
| [02](papers/02-crime-panel/) | Does deterrence lower crime? County panel | Cornwell & Trumbull, 90 counties × 7 years | Arrest elasticity falls from −0.633 (pooled) to −0.360 (two-way FE); clustering doubles the errors |
| [03](papers/03-religion-and-domestic-violence/) | Does evangelical density go with recorded domestic violence? | SINAN, IBGE Census and GDP, IBGE API | No robust association; recorded rates follow how much a municipality notifies |
| [04](papers/04-fund-selection/) | Picking funds for a retail menu: do past winners repeat, and what do fees cost? | CVM open data (daily reports, factsheets, registers), CDI | Past returns barely help; each point of fees costs 0.74 points a year in equity funds; an AI-written committee memo, checked twice |

Each paper's README is one page, in the same order: question, data, specification and refinement, result, AI review.
Each paper also has a `final-report.pdf` that the pipeline builds from its own outputs: the question and result, the
data-check summary, the main tables and the main figures. Running the pipeline again rebuilds it (byte for byte, if the
outputs did not change).

## Data checks

Every paper has a checks script that runs between building the base and the first regression, and writes
`output/data_checks.json` with the input fingerprints (SHA-256) and one line per check: missing values, gaps in
dates, units, ranges, duplicates, panel balance, merge coverage, and codes against the official IBGE list.
A FAIL stops the run; a WARN is reported. Current state: 48 pass, 9 warnings, 0 fail. Examples of what they caught:
in 03, 43% of municipalities have a year with no record, and the original code averaged their rate over the years that
exist (the paper now re-estimates with the full 3-year denominator; the conclusion holds); also in 03, the coursework
version matched census and GDP tables by name and silently lost São Paulo, Rio de Janeiro and Brasília (a new check now
requires all 27 state capitals; the inputs are now downloaded by the code and all 5,565 municipalities match); in 04, the public fund data
carry admin fees of up to 90,000% a year and expense ratios in the millions (unit errors), zero quotas and ±50% monthly
jumps, all counted and excluded before any model.

## AI reviewer

`python -m aecon.review` reads the *Result* section of each paper README and the paper's tables.

1. **Python** extracts every number from the LaTeX tables and stats files (~130–170 cells per paper, with captions)
   and splits the text into statements.
2. **The model** (Claude Haiku 5.5, structured JSON output validated by a JSON Schema) maps each number in a statement to
   a table cell and judges the reading: significance against the stars, sign, standard error vs coefficient, elasticity
   vs percentage points, IRR, causal wording on associational designs, "proves" from a non-rejection.
3. **Python** re-checks every mapped number against its cell, up to the rounding shown on each side. A number is never
   declared correct on the model's word; if the model points at a cell that does not hold the number, Python overrides it.

**Golden set** (`golden/statements.json`): 30 statements, 18 with a planted error (wrong digit, wrong value, standard
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
about US$ 0.004. Hard cap of 20 calls per run,
60 s timeout, SDK retries for network errors, one retry when the answer fails the schema or the checker (e.g. a number
that is not in the statement), one JSON log line per call with tokens. Answers are recorded in `recordings/`: the same
request is never paid twice, and without a key the reviewer replays them (demo mode, used by the tests).
The key is read from `ANTHROPIC_API_KEY` or a local `.env` (see `.env.example`) and never printed or committed.

## Run

Python 3.10+ (tested on 3.14, Windows 11).

```bash
pip install -r requirements.txt
python run_all.py              # every paper: base, checks, models, tables, final-report.pdf; then the snapshot check
python run_all.py --download   # papers 01 and 04 pull their data again (BCB, CVM: ~750 MB; changes the numbers)
python run_all.py --review     # also the AI reviewer and the AI committee memo (live with a key, recorded without)
python -m pytest               # 26 tests, no API calls
```

`run_all.py` ends by comparing the 13 tables of papers 01 and 02 with the versions submitted for grading
(`tests/table_snapshot.json`): they are byte-for-byte identical. Paper 03 now runs on inputs this repository downloads
itself, so its tables differ from the coursework version (16 more municipalities; same conclusion).

## Origin and role

Papers 01–03 started as Econometrics I coursework (B.Sc. in Economics, Federal University of Rio de Janeiro, first
semester of 2026), written in a group. Only my parts are here; the reports with my teammates' names are not.
- **01: all of it.** Data pipeline, estimation and diagnostics code, tables, figures and the interpretation.
- **02: the code.** Panel set-up, every estimation, the packaged tests and every table and figure. The by-hand test
  calculations and the written interpretation were a teammate's and are not published; the README here is mine.
- **03: I finished it.** The topic and a first pipeline came from a teammate; neither that code nor the data files
  downloaded for it are here. I re-scoped the design when the data could not support it, wrote the aggregation, base and
  analysis code in this folder, ran the estimation, the robustness checks and the AI review loop.

The AI review layer, the data checks, the refinement in 03, paper 04 and this structure were added afterwards. Paper 04
uses only public CVM and BCB data.
The coursework rule for 01 and 02 allowed AI only for code support; the econometric choices and interpretation are mine.
03 required AI: the decision log and the four adversarial AI reviews are in
`papers/03-religion-and-domestic-violence/ai_trail/` (Portuguese). Code comments and table labels are in Portuguese, as submitted.

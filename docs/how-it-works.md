# How it works

The detail behind the README: the pipeline, the data, where each study comes from, and what was measured.

## How I use it

- **While doing the coursework (2026):** I wrote the code with Claude as a coding assistant, one numbered script per
  step. For each modelling choice I wrote down why (monthly or 12-month inflation, ADF and KPSS together, how to deal
  with autocorrelation); those notes became the "Specification and refinement" table in each study's `method.md`.
  Study 03 required AI: I ran the research with an agent workflow and four adversarial AI reviews; the decision log and
  the reviews are in [papers/03-religion-and-domestic-violence/ai_trail/](../papers/03-religion-and-domestic-violence/ai_trail/).
- **Before handing it in:** I reran everything in a clean environment to check that it reproduced. That run found a
  broken dependency pin that would have stopped the grader's run. The same check is now automatic: every run compares
  each table with its stored fingerprint.
- **For the oral exam:** I turned my own doubts about each result into flashcards.
- **Now:** nothing runs on a schedule. I run a study again when I change the code or when new data is out
  (`python run_all.py --download`), look at what changed, and run the AI reviewer if the write-up changed. Study 04 was
  built this way from scratch, and the same pattern (data checks before the model, recorded AI answers, a reviewer
  measured against known answers) is the one I reuse in my other repositories.

## Pipeline

1. **Collect:** each paper downloads its own data from public APIs and keeps the raw files, so it also runs offline.
2. **Check:** a checks script runs between building the base and the first regression and writes
   `output/data_checks.json` (missing values, date gaps, units, ranges, duplicates, merge coverage, official codes).
   A FAIL stops the run.
3. **Model:** each study's `method.md` has a table "Specification and refinement": every step, why it was taken, what it showed.
4. **Report:** `run_all.py` writes the tables, the figures and `final-reports/<paper>.pdf`, then compares each table
   with its stored fingerprint.
5. **Review:** an AI reviewer checks each number in the write-up against the tables and each coefficient reading;
   Python re-checks every number the model matched. Details: [ai-reviewer.md](ai-reviewer.md).

## Data

| Paper | Source | In the repository |
|---|---|---|
| 01 | BCB APIs: IPCA (SGS 433), PNAD unemployment (SGS 24369), Focus expectations | raw series, 2012-2026 |
| 02 | Cornwell & Trumbull crime panel, from the `wooldridge` package | loaded at run time |
| 03 | SINAN notifications (Ministry of Health), IBGE Census 2010 and GDP (SIDRA), IBGE localities API | IBGE tables and the SINAN municipality-year aggregate; not the raw SINAN extract (692 MB) |
| 04 | CVM daily fund reports, factsheets and registers; CDI (SGS 4391) | menus and month-end quotas (7 MB); not the raw CVM files (~750 MB) |

Everything is public data. Nothing comes from a client, an employer or a private portfolio.

## Results in numbers

| Paper | Question | Headline | Report |
|---|---|---|---|
| [01](../papers/01-phillips-curve/) | Is there a Phillips-curve trade-off in Brazil, 2012-2026? | No: inflation follows inertia (0.398) and expectations (0.686); a vertical long-run curve is not rejected (p = 0.432) | [PDF](../final-reports/01-phillips-curve.pdf) |
| [02](../papers/02-crime-panel/) | Does deterrence lower crime? (90 counties × 7 years) | Arrest elasticity falls from −0.633 (pooled) to −0.360 (two-way fixed effects); clustering doubles the errors | [PDF](../final-reports/02-crime-panel.pdf) |
| [03](../papers/03-religion-and-domestic-violence/) | Does evangelical density go with recorded domestic violence? | No robust association (0.0009, p = 0.325, 5,046 municipalities); recorded rates follow notification intensity | [PDF](../final-reports/03-religion-and-domestic-violence.pdf) |
| [04](../papers/04-fund-selection/) | Picking retail funds: do past winners repeat, and what do fees cost? | Past returns barely help; each point of expense ratio costs 0.735 points a year in equity funds | [PDF](../final-reports/04-fund-selection.pdf) |

- **AI reviewer:** checks that every number in each write-up matches its table cell and that each coefficient is read
  correctly; on the four write-ups, 60 numbers checked, 0 flags (`papers/*/output/review.md`).
- **Data checks:** 48 pass, 9 warnings, 0 fail. One of them stopped a silent merge error in paper 03: the graded
  version had lost São Paulo, Rio de Janeiro and Brasília in a name match.
- **Reproducible:** the 13 tables of papers 01-02 are byte-identical to the versions submitted for grading; every run
  rebuilds identical tables, figures and PDFs. A fingerprint of every table is stored in `tests/table_snapshot.json`,
  and each run compares the new tables with it.

![Fees and next-year returns (paper 04)](../papers/04-fund-selection/output/fig_costs.png)

## Origin and role

Studies 01-03 come from Econometrics I coursework (B.Sc. in Economics, Federal University of Rio de Janeiro, 2026),
written in a group; only my parts are here, and each final report extracts the quantitative work of a longer paper (the
full papers are available on request). Study 04 was built for this portfolio from public CVM data. 01 is all mine. In 02 I wrote all the code; the written interpretation was a
teammate's and is not published. In 03 the topic and a first pipeline came from a teammate, and neither that code nor
its data files are here; I re-scoped the design, wrote the code in this folder, and ran the estimation and the AI review
loop. The data checks, the AI reviewer, the refinements in 03 and paper 04 were added afterwards. The coursework code was
later translated to English (names, comments, layout); it is the same code, and the table-fingerprint test shows the tables
did not change.

## Commands

```bash
python run_all.py              # all studies
python run_all.py 03           # one study
python run_all.py --review     # also the AI reviewer and the committee memo
python run_all.py --download   # pull the data again (changes the numbers)
python -m pytest
```

What to do when a download or a check fails: [RUNBOOK.md](../RUNBOOK.md).

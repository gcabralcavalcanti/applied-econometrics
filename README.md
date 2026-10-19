# Applied econometrics

Four short empirical papers built the same way: Python pulls public data, automatic checks gate every regression, each
specification step has a stated reason, and an AI reviewer checks every number in the write-up against the tables.

![Public data only](https://img.shields.io/badge/data-public%20only-2a78d6)
![Built with AI assistance](https://img.shields.io/badge/built%20with-AI%20assistance-52514e)

## Results

| Paper | Question | Headline | Report |
|---|---|---|---|
| [01](papers/01-phillips-curve/) | Is there a Phillips-curve trade-off in Brazil, 2012–2026? | No: inflation follows inertia (0.398) and expectations (0.686); a vertical long-run curve is not rejected (p = 0.432) | [PDF](final-reports/01-phillips-curve.pdf) |
| [02](papers/02-crime-panel/) | Does deterrence lower crime? (90 counties × 7 years) | Arrest elasticity falls from −0.633 (pooled) to −0.360 (two-way fixed effects); clustering doubles the errors | [PDF](final-reports/02-crime-panel.pdf) |
| [03](papers/03-religion-and-domestic-violence/) | Does evangelical density go with recorded domestic violence? | No robust association (0.0009, p = 0.325, 5,046 municipalities); recorded rates follow notification intensity | [PDF](final-reports/03-religion-and-domestic-violence.pdf) |
| [04](papers/04-fund-selection/) | Picking retail funds: do past winners repeat, and what do fees cost? | Past returns barely help; each point of expense ratio costs 0.735 points a year in equity funds | [PDF](final-reports/04-fund-selection.pdf) |

- **AI reviewer:** caught 18 of 18 planted errors on a 30-statement golden set, with 0 false alarms; on the four
  write-ups, 60 numbers checked and 0 flags (`reports/`).
- **Data checks:** 48 pass, 9 warnings, 0 fail. One of them stopped a silent merge error in paper 03: the graded
  version had lost São Paulo, Rio de Janeiro and Brasília in a name match.
- **Reproducible:** the 13 tables of papers 01–02 are byte-identical to the versions submitted for grading; every run
  rebuilds identical tables, figures and PDFs (`tests/table_snapshot.json`).

![Fees and next-year returns (paper 04)](papers/04-fund-selection/output/fig_costs.png)

## Run it

```bash
pip install -r requirements.txt
python run_all.py              # every paper: base, data checks, models, tables, final-reports/*.pdf
python run_all.py --review     # also the AI reviewer and the AI committee memo (recorded answers, no key needed)
python run_all.py --download   # pull the data again from the BCB, IBGE and CVM APIs (changes the numbers)
python -m pytest               # 26 tests, no API calls
```

Python 3.10+ (tested on 3.14, Windows 11). With `ANTHROPIC_API_KEY` set (or a `.env`, see `.env.example`) the reviewer
calls the API; without it, it replays the answers in `recordings/`.

## How it works

1. **Collect:** each paper downloads its own data from public APIs and keeps the raw files, so it also runs offline.
2. **Check:** a checks script runs between building the base and the first regression and writes
   `output/data_checks.json` (missing values, date gaps, units, ranges, duplicates, merge coverage, official codes).
   A FAIL stops the run.
3. **Model:** each paper README has a table "Specification and refinement": every step, why it was taken, what it showed.
4. **Report:** `run_all.py` writes the tables, the figures and `final-reports/<paper>.pdf`, then compares the tables
   with the snapshot.
5. **Review:** Python extracts every number from the tables; Claude Haiku maps each number in the write-up to a cell and
   judges the reading (significance, sign, units, causal wording); Python re-checks every mapped number.
   Details, and how the golden-set score was reached: [docs/ai-reviewer.md](docs/ai-reviewer.md).

## Data

| Paper | Source | In the repository |
|---|---|---|
| 01 | BCB APIs: IPCA (SGS 433), PNAD unemployment (SGS 24369), Focus expectations | raw series, 2012–2026 |
| 02 | Cornwell & Trumbull crime panel, from the `wooldridge` package | loaded at run time |
| 03 | SINAN notifications (Ministry of Health), IBGE Census 2010 and GDP (SIDRA), IBGE localities API | IBGE tables and the SINAN municipality-year aggregate; not the raw SINAN extract (692 MB) |
| 04 | CVM daily fund reports, factsheets and registers; CDI (SGS 4391) | menus and month-end quotas (7 MB); not the raw CVM files (~750 MB) |

Everything is public data. Nothing comes from a client, an employer or a private portfolio.

## Limits

- All four papers are associational; none claims a causal effect.
- Paper 04 covers 2021–2025 only (four year pairs), and the factsheet file thins out after CVM Resolution 175.
- The reviewer checks the write-up against the tables; it does not judge whether a model is the right one.
- Table labels in papers 01–03 are in Portuguese, as graded.

## Origin and role

Papers 01–03 started as Econometrics I coursework (B.Sc. in Economics, Federal University of Rio de Janeiro, 2026),
written in a group; only my parts are here. 01 is all mine. In 02 I wrote all the code; the written interpretation was a
teammate's and is not published. In 03 the topic and a first pipeline came from a teammate, and neither that code nor
its data files are here; I re-scoped the design, wrote the code in this folder, and ran the estimation and the AI review
loop. The data checks, the AI reviewer, the refinements in 03 and paper 04 were added afterwards. The coursework code was
later translated to English (names, comments, layout); it is the same code, and the snapshot test shows the tables
did not change.

## How AI was used

I use Claude (Claude Code and the API) for coding, review and documentation. The questions, modelling choices,
validation and conclusions are mine. Paper 03 required AI by design; its decision log and the AI reviews are in
`papers/03-religion-and-domestic-violence/ai_trail/`.

## License

MIT — see [LICENSE](LICENSE).

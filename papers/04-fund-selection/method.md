# 04 · Picking funds from a retail menu: does past performance help, and what do fees cost?: how it was built

## Data
| Input | Source (pulled by `code/01_fetch_and_build.py`) | What it gives |
|---|---|---|
| Daily fund reports, 2021-01 to 2026-09 (69 files, ~730 MB) | CVM open data, `INF_DIARIO` | month-end quota and net assets of every fund |
| Fund factsheets (lâminas), December 2021-2025 | CVM open data, `LAMINA` | admin fee, expense ratio, performance fee; only retail funds file one |
| Fund registers, old and CVM Resolution 175 | CVM open data, `CAD` | asset class: equity, multi-asset, fixed income |
| CDI, monthly | BCB SGS series 4391 | the benchmark a saver gets for free |

The **menu** at the end of year y is every fund with a December-y factsheet: the funds a retail investor could
actually buy then, with the fees stated then. Building it date by date keeps funds that later closed in the sample.
Only month-end quotas of menu funds are kept (`data/monthly_quotas.csv.gz`), so the paper runs offline.

`code/02_checks.py` writes `output/data_checks.json` (7 pass, 5 warnings, 0 fail). The warnings are real problems of the
public data, each handled in the analysis: 54 admin fees outside 0-5% a year (up to 90,000, a unit error) and 860
expense ratios outside 0-10% (negative or in the millions) are set to missing; 1,780 fund-months with a zero quota
(funds being wound up) and 1,303 month-end returns beyond ±50% (splits, typos) are dropped; and after Resolution 175
far fewer factsheets reach the open-data file (about 4,700 funds a year in 2021-2023, about 1,100 in 2024-2025).

## Specification and refinement
| Step | Why | What it showed |
|---|---|---|
| Excess return over the CDI, from quotas | quotas are net of every fee, so this is what the investor got | most fund-years trail the CDI |
| Point-in-time menu (December factsheet) | a menu built from today's survivors overstates both returns and persistence | 13,610 fund-years, 5,221 funds |
| Quintiles of this year's return, mean of next year's, equal weight per year pair | the committee's question in its own terms | no monotonic pattern |
| Slope of next year on this year, clustered by fund | uses all funds, not just the extremes | small positive slopes |
| Transition: share of the top quintile that stays on top | compares with the 20% a coin toss gives | some persistence, strongest in fixed income |
| Next-year excess on the expense ratio, with size, performance-fee dummy and year effects | net returns already subtract fees, so a slope of −1 means fees are a pure cost | equity and multi-asset pay for their fees |
| Monte Carlo of four rules over 10 years | turns the estimates into the wealth an investor ends with | cheap funds beat the random pick in every class |

## AI memo for the committee
`code/04_memo.py`: Claude writes the memo from the four tables, citing a cell for every number. Python rejects a draft
whose numbers are not in the cells it cites; the reviewer checks each finding; flagged findings go back to the writer
once. Current memo: 6 findings, none flagged (`output/committee_memo.md`). During development a first draft read the
persistence table backwards and the reviewer caught it; the case is in [docs/memo-draft-caught.md](../../docs/memo-draft-caught.md).
Cost of the memo with its review: about US$ 0.004.

## Run
`python run_all.py 04` (offline from `data/`) · `python code/01_fetch_and_build.py` to pull everything again from the CVM. Summary with the main tables and figures: [final-reports/04-fund-selection.pdf](../../final-reports/04-fund-selection.pdf).
All inputs are public CVM and BCB data.

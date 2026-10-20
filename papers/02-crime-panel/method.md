# 02 · Crime and deterrence: a county panel: how it was built

## Data
`crime4` (Cornwell & Trumbull 1994): 90 North Carolina counties, 1981-1987, 630 county-years. It is loaded from the
`wooldridge` Python package, so the paper runs offline. `code/q3_checks.py` runs after the panel is built and before
any regression, and writes `output/data_checks.json` (10 pass, 2 warnings):
balanced 90 × 7 panel, no duplicate county-year, no missing values in the regression variables, every log variable
equal to the log of its level, plausible ranges. The two warnings are real quirks of this dataset: the "probability" of
arrest exceeds 1 in 5 county-years (max 2.75) and the "probability" of conviction in 71 (max 37). They are ratios of
counts (arrests/offences, convictions/arrests), not probabilities; logs keep them usable, but they are worth knowing
before reading the coefficients.

## Specification and refinement
The sequence follows the assignment; I wrote all the code and the tables. Each step answers a weakness of the one before.

| Step | Why | What it showed |
|---|---|---|
| Pooled OLS in logs | coefficients read as elasticities | strong deterrence: arrest −0.633 |
| Breusch-Pagan and White tests | squared residuals fan out with the fitted values | heteroskedasticity is clear |
| HC1 robust errors | valid inference without modelling the variance | standard errors rise, coefficients unchanged |
| County fixed effects | fixed traits (culture, reporting, urbanisation) bias pooled OLS | arrest elasticity falls to −0.395 |
| Year effects too (two-way) | statewide shocks hit every county in the same year | −0.360; police per capita stays +0.422 |
| Errors clustered by county | the same county's errors are correlated over the years | standard errors roughly double |

## AI review
`python -m applied_econometrics.review` checks every sentence of the README's Result section against the tables: see [output/review.md](output/review.md).

## Run
`python run_all.py 02` · tables in `output/` (LaTeX, decimal comma, as submitted), figures as PDF and PNG. Summary with the main tables and figures: [final-reports/02-crime-panel.pdf](../../final-reports/02-crime-panel.pdf).

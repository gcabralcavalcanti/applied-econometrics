# 02 · Crime and deterrence: a county panel

> The final report ([final-reports/02-crime-panel.pdf](../../final-reports/02-crime-panel.pdf)) is generated automatically from the code's outputs. The main output is the quantitative part: data, checks, models and tables. It extracts the quantitative work of a longer paper I wrote for a UFRJ econometrics course; the full paper is available on request.

## Question
Do counties with a higher probability of arrest, conviction and prison have less crime, and how much of the answer
changes once fixed county traits, common year shocks and serial correlation are handled?

## Data
`crime4` (Cornwell & Trumbull 1994): 90 North Carolina counties, 1981–1987, 630 county-years. It is loaded from the
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
| Breusch–Pagan and White tests | squared residuals fan out with the fitted values | heteroskedasticity is clear |
| HC1 robust errors | valid inference without modelling the variance | standard errors rise, coefficients unchanged |
| County fixed effects | fixed traits (culture, reporting, urbanisation) bias pooled OLS | arrest elasticity falls to −0.395 |
| Year effects too (two-way) | statewide shocks hit every county in the same year | −0.360; police per capita stays +0.422 |
| Errors clustered by county | the same county's errors are correlated over the years | standard errors roughly double |

## Result
| Specification | log P(arrest) | log police per capita |
|---|---|---|
| Pooled OLS | -0.633 | 0.352 |
| County fixed effects | -0.395 | 0.422 |
| Two-way fixed effects | -0.360 | 0.422 |

- Breusch–Pagan LM = 191.60 and White LM = 410.04, both with p < 0.0001: heteroskedasticity is clear.
- In the two-way model, clustering by county raises the standard error on the arrest elasticity from 0.033 to 0.064.
- On police per capita the clustered standard error is 0.093, against 0.027 before. Both coefficients keep three stars after clustering.
- Fixed effects cut the pooled arrest elasticity by about a third, so part of the pooled deterrence was county traits.

Reading: higher arrest probability goes with less crime even within a county. The positive police coefficient is the
classic simultaneity sign (counties hire police where crime is high), so none of this is a causal estimate.

## AI review
`python -m applied_econometrics.review` checks every sentence above against the tables: see [output/review.md](output/review.md).

## Run
Runs without an API key, replaying recorded answers. Set `ANTHROPIC_API_KEY` to call Claude live.

`python run_all.py 02` · tables in `output/` (LaTeX, decimal comma, as submitted), figures as PDF and PNG. Summary with the main tables and figures: [final-reports/02-crime-panel.pdf](../../final-reports/02-crime-panel.pdf).

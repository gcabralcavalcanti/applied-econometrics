# 01 · Is there a Phillips-curve trade-off in Brazil? (2012-2026): how it was built

## Data
| Series | Source (pulled by `code/q2_1_download_series.py`) | Unit |
|---|---|---|
| IPCA inflation | Central Bank of Brazil SGS API, series 433 | % per month |
| Unemployment | SGS series 24369 (PNAD Contínua) | % of labour force |
| Expected inflation for t+1 | BCB Focus survey API (`ExpectativaMercadoMensais`), median of the last survey in month t | % per month |

The raw downloads ship in `tmp/`, so the published numbers reproduce offline; `python run_all.py --download` refreshes them.
`code/q2_checks.py` runs before any regression and writes `output/data_checks.json` (17 pass, 1 warning):
month continuity in every series, IPCA in monthly (not 12-month) units, a t+1 Focus reading for every month,
expectation and IPCA on the same scale, no duplicates, and a warning that the COVID months sit inside the window.

## Specification and refinement
| Step | Why | What it showed |
|---|---|---|
| Monthly IPCA, not 12-month | same unit as the monthly Focus expectation; 12-month inflation is almost non-stationary | noisier, but clean for stationarity |
| Static OLS, π on u | the textbook trade-off | flat line; Durbin-Watson 0.927 signals omitted dynamics |
| ADF and KPSS together | opposite null hypotheses, so neither test decides alone | IPCA stationary; unemployment and expectations persistent with mixed evidence; no spurious-regression symptom (R² ≈ 0) |
| Breusch-Godfrey and Ljung-Box (12 lags) | Durbin-Watson only sees first order and has an inconclusive zone | strong autocorrelation in the static model |
| Dynamic model: add π(t−1) and E_t[π(t+1)] | the fix for omitted dynamics, not differencing (IPCA is already I(0)) | R² 0.000 → 0.421 |
| Breusch-Godfrey, not Durbin-Watson, after adding the lag | DW is biased towards 2 with a lagged dependent variable | first-order autocorrelation gone, seasonal structure left |
| Newey-West errors, L = 4 (and 8, 12) | consistent standard errors under the remaining autocorrelation | same conclusions for every L |
| Test γ + δ = 1 | the natural-rate hypothesis: a vertical long-run curve | not rejected |
| Seasonal dummies, no-COVID sample, linear trend | the three obvious objections | conclusions unchanged |

## AI review
`python -m applied_econometrics.review` checks every sentence of the README's Result section against the tables: see [output/review.md](output/review.md).

## Run
`python run_all.py 01` · tables in `output/` (LaTeX, as submitted), figures as PDF. Table labels are in Portuguese, as graded. Summary with the main tables and figures: [final-reports/01-phillips-curve.pdf](../../final-reports/01-phillips-curve.pdf).

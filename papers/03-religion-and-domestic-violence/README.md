# 03 · Evangelical density and recorded domestic violence in Brazilian municipalities

## Question
Do municipalities with a larger share of evangelicals record more (or less) domestic violence against women?

## Data
| Input | Source | Unit |
|---|---|---|
| Domestic-violence notifications, 2009–2019 | Ministry of Health, SINAN (via basedosdados), aggregated by `code/00_agrega_sinan.py` | cases per municipality-year |
| Population and evangelicals | IBGE Census 2010, SIDRA table 2094 | persons |
| GDP per municipality | IBGE, municipal GDP 2010 | R$ |
| Official list of municipalities | IBGE localities API, pulled by `code/q4_checks.py` | code and name |

The raw SINAN extract (~692 MB) is not in the repo; its municipality-year aggregate is (`tmp/sinan_mun_ano.csv`).
`code/q4_checks.py` runs after the base is built and before any regression, and writes `output/data_checks.json`
(13 pass, 1 warning): SINAN year range, counts consistent (female ≤ domestic ≤ total), the 0/1 sex coding producing
female victims, 7-digit codes, merge coverage, every code in the base being an official municipality in the IBGE API,
names matching the official names, density within 0–100%. The warning led to the refinement below.

## Specification and refinement
| Step | Why | What it showed |
|---|---|---|
| Rate per 1,000 residents, 2011–2013 average | one year is too noisy for small towns | 15.4% of municipalities still record zero |
| OLS with state fixed effects, HC1 errors | states differ in health systems and reporting; the White test rejects homoskedasticity | no association |
| Quadratic and log(1+y) forms | the link could be non-linear or driven by outliers | no association |
| Non-domestic notification proxy | SINAN records violence where the health network reports it; a municipality that notifies more of everything records more domestic violence too | R² jumps from 0.170 to 0.440; evangelical density unchanged |
| WLS by population, Poisson with population offset | small towns dominate OLS; counts with many zeros | coefficient turns negative, still insignificant |
| Robustness: other window, no capitals, clustered by state, population ≥ 5k, rolling 3-year windows | the obvious objections | nothing robust |
| **Added after submission:** divide by 3 years, not by the years on record | the data check found that 43.0% of municipalities have a year with no record, and the original code averaged over the years that exist, overstating their rate | coefficient 0.0007 (p = 0.411); conclusion unchanged |

Mistakes caught in the AI-assisted process (full trail in `ai_trail/`): a made-up citation; SINAN codes sex as 0/1, so
filtering on 'F' counted zero victims; a design the data could not support (broadband data starts in 2021, SINAN ends in
2019); a tautological regressor that pushed R² to 0.76.

## Result
- With state fixed effects and HC1 errors, the evangelical-density coefficient is 0.0009 (SE 0.0009, p = 0.318), on 5030 municipalities.
- Adding the non-domestic notification proxy raises R² from 0.170 to 0.440; the proxy coefficient is 0.4244, significant at 1%, and evangelical density stays at 0.0009.
- The Poisson model with a population offset gives -0.0077, an incidence-rate ratio of 0.9923, not significant.
- In WLS the coefficient turns negative (-0.0028), not significant.
- Across the six robustness columns, the coefficient reaches significance only once: at 10%, with errors clustered by state (0.0009*).
- With the 3-year denominator the coefficient is 0.0007 (p = 0.411).

Reading: no robust association. What explains recorded rates is how much a municipality notifies, not its religious
composition. Associational, not causal; the denominator is the whole population, not women at risk.

## AI review
`python -m aecon.review` checks every sentence above against the tables: see `reports/review_03-religion-and-domestic-violence.md`.

## Run
`python run_all.py 03` · tables in `output/tables/`, figures in `output/figures/`. The AI trail is in Portuguese.

# 03 · Evangelical density and recorded domestic violence in Brazilian municipalities: how it was built

## Data
| Input | Source | Unit |
|---|---|---|
| Domestic-violence notifications, 2009-2019 | Ministry of Health, SINAN microdata (public, via basedosdados), aggregated by `code/00_aggregate_sinan.py` | cases per municipality-year |
| Population and evangelicals | IBGE Census 2010, SIDRA table 2094, pulled by `code/00_download_ibge.py` | persons |
| GDP per municipality, 2010 | IBGE SIDRA table 5938, pulled by `code/00_download_ibge.py` | R$ |
| Official list of municipalities | IBGE localities API, pulled by `code/q4_checks.py` | code and name |

The raw SINAN extract (~692 MB, the public `br_ms_sinan` microdata downloaded from basedosdados) is not in the repo;
all the processing is done by the code here. Its municipality-year aggregate, produced by `00_aggregate_sinan.py`,
is (`tmp/sinan_mun_ano.csv`). `code/q4_checks.py` runs after the base is built and before any regression, and writes
`output/data_checks.json` (14 pass, 1 warning): SINAN year range, counts consistent (female ≤ domestic ≤ total), the 0/1
sex coding producing female victims, 7-digit codes, merge coverage, all 27 state capitals present, every code an
official municipality in the IBGE API, names matching the official names, density within 0-100%.

## Specification and refinement
| Step | Why | What it showed |
|---|---|---|
| Rate per 1,000 residents, 2011-2013 average | one year is too noisy for small towns | 15.3% of municipalities still record zero |
| OLS with state fixed effects, HC1 errors | states differ in health systems and reporting; the White test rejects homoskedasticity | no association |
| Quadratic and log(1+y) forms | the link could be non-linear or driven by outliers | no association |
| Non-domestic notification proxy | SINAN records violence where the health network reports it; a municipality that notifies more of everything records more domestic violence too | R² jumps from 0.171 to 0.439; evangelical density unchanged |
| WLS by population, Poisson with population offset | small towns dominate OLS; counts with many zeros | not significant either |
| Robustness: other window, no capitals, clustered by state, population ≥ 5k, rolling 3-year windows | the obvious objections | nothing robust |
| **Inputs pulled by this code (after submission)** | the census and GDP files are now downloaded from the IBGE API by `00_download_ibge.py` | the coursework version matched the two tables by municipality name and lost 16 municipalities, among them São Paulo, Rio de Janeiro and Brasília (10.9% of the population); now all 5,565 match and the new capitals check would have stopped the old run. OLS is unchanged; WLS and Poisson, which weight by population, turn from negative to positive, still not significant |
| **3-year denominator (after submission)** | the data checks found that 43.0% of municipalities have a year with no record, and the code averaged over the years that exist, overstating their rate | coefficient 0.0007 (p = 0.414); conclusion unchanged |

Mistakes caught in the AI-assisted process (decision log in `ai_trail/MEMORY.md`): a made-up citation; SINAN codes sex as
0/1, so filtering on 'F' counted zero victims; a design the data could not support (broadband data starts in 2021, SINAN
ends in 2019); a tautological regressor that pushed R² to 0.76.

## AI review
`python -m applied_econometrics.review` checks every sentence of the README's Result section against the tables: see [output/review.md](output/review.md).

## Run
`python run_all.py 03` · `python code/00_download_ibge.py` pulls the IBGE inputs again · tables in `output/tables/`,
figures in `output/figures/`, summary in [final-reports/03-religion-and-domestic-violence.pdf](../../final-reports/03-religion-and-domestic-violence.pdf). The decision log and the AI reviews are in Portuguese.

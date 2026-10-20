# 02 · Crime and deterrence: a county panel

> The final report ([final-reports/02-crime-panel.pdf](../../final-reports/02-crime-panel.pdf)) is generated automatically from the code's outputs. The main output is the quantitative part: data, checks, models and tables. It extracts the quantitative work of a longer paper I wrote for a UFRJ econometrics course; the full paper is available on request.

## Run this study

```bash
python run_all.py 02   # only this study: data checks, models, tables and final-reports/02-crime-panel.pdf
```

Runs without an API key, replaying recorded answers. Set `ANTHROPIC_API_KEY` to call Claude live.

## Question
Do counties with a higher probability of arrest, conviction and prison have less crime, and how much of the answer
changes once fixed county traits, common year shocks and serial correlation are handled?

## Result
| Specification | log P(arrest) | log police per capita |
|---|---|---|
| Pooled OLS | -0.633 | 0.352 |
| County fixed effects | -0.395 | 0.422 |
| Two-way fixed effects | -0.360 | 0.422 |

- Breusch-Pagan LM = 191.60 and White LM = 410.04, both with p < 0.0001: heteroskedasticity is clear.
- In the two-way model, clustering by county raises the standard error on the arrest elasticity from 0.033 to 0.064.
- On police per capita the clustered standard error is 0.093, against 0.027 before. Both coefficients keep three stars after clustering.
- Fixed effects cut the pooled arrest elasticity by about a third, so part of the pooled deterrence was county traits.

Reading: higher arrest probability goes with less crime even within a county. The positive police coefficient is the
classic simultaneity sign (counties hire police where crime is high), so none of this is a causal estimate.

## More
- [How it was built](method.md): data, data checks, every modelling step and why.
- [Final report (PDF)](../../final-reports/02-crime-panel.pdf) · [AI review of this page](output/review.md)

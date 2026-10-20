# 01 · Is there a Phillips-curve trade-off in Brazil? (2012-2026)

> The final report ([final-reports/01-phillips-curve.pdf](../../final-reports/01-phillips-curve.pdf)) is generated automatically from the code's outputs. The main output is the quantitative part: data, checks, models and tables. It extracts the quantitative work of a longer paper I wrote for a UFRJ econometrics course; the full paper is available on request.

## Run this study

```bash
python run_all.py 01   # only this study: data checks, models, tables and final-reports/01-phillips-curve.pdf
```

Runs without an API key, replaying recorded answers. Set `ANTHROPIC_API_KEY` to call Claude live.

## Question
Does higher unemployment go with lower inflation in Brazil, once inflation inertia and expectations are in the model?

## Result
- In the static model the unemployment coefficient is -0.002 (SE 0.010), with no stars: no static trade-off.
- In the dynamic model, lagged inflation has a coefficient of 0.398 and the Focus expectation 0.686, both significant at 1%; unemployment stays insignificant at 0.007.
- R² rises from 0.000 to 0.421, on 169 monthly observations.
- H0: γ + δ = 1 is not rejected (p = 0.432): the data do not reject a vertical long-run Phillips curve.
- With Newey-West errors the standard error on the expectation term rises from 0.111 to 0.177; it stays significant.
- With seasonal dummies the expectation coefficient is 0.783 and R² 0.523; without the COVID months unemployment is 0.001.

Reading: Brazilian inflation is driven by inertia and expectations; labour-market slack barely shows up. Descriptive, not causal: expectations are endogenous and the model uses the unemployment rate, not the gap to its natural rate.

## More
- [How it was built](method.md): data, data checks, every modelling step and why.
- [Final report (PDF)](../../final-reports/01-phillips-curve.pdf) · [AI review of this page](output/review.md)

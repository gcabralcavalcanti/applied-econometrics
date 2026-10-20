# 03 · Evangelical density and recorded domestic violence in Brazilian municipalities

> The final report ([final-reports/03-religion-and-domestic-violence.pdf](../../final-reports/03-religion-and-domestic-violence.pdf)) is generated automatically from the code's outputs. The main output is the quantitative part: data, checks, models and tables. It extracts the quantitative work of a longer paper I wrote for a UFRJ econometrics course; the full paper is available on request.

## Run this study

```bash
python run_all.py 03   # only this study: data checks, models, tables and final-reports/03-religion-and-domestic-violence.pdf
```

Runs without an API key, replaying recorded answers. Set `ANTHROPIC_API_KEY` to call Claude live.

## Question
Do municipalities with a larger share of evangelicals record more (or less) domestic violence against women?

## Result
- With state fixed effects and HC1 errors, the evangelical-density coefficient is 0.0009 (SE 0.0009, p = 0.325), on 5046 municipalities.
- Adding the non-domestic notification proxy raises R² from 0.171 to 0.439; the proxy coefficient is 0.4237, significant at 1%, and evangelical density stays at 0.0009.
- The Poisson model with a population offset gives 0.0080, an incidence-rate ratio of 1.0081, not significant.
- In WLS the coefficient is 0.0019, not significant.
- Across the six robustness columns, the coefficient reaches significance only once: at 10%, with errors clustered by state (0.0009*).
- With the 3-year denominator the coefficient is 0.0007 (p = 0.414).

Reading: no robust association. What explains recorded rates is how much a municipality notifies, not its religious
composition. Associational, not causal; the denominator is the whole population, not women at risk.

## More
- [How it was built](method.md): data, data checks, every modelling step and why.
- [Final report (PDF)](../../final-reports/03-religion-and-domestic-violence.pdf) · [AI review of this page](output/review.md)

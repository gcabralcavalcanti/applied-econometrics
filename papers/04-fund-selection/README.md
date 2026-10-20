# 04 · Picking funds from a retail menu: does past performance help, and what do fees cost?

> The final report ([final-reports/04-fund-selection.pdf](../../final-reports/04-fund-selection.pdf)) is generated automatically from the code's outputs. The main output is the quantitative part: data, checks, models and tables. This study was built for this portfolio from public CVM data.

## Run this study

```bash
python run_all.py 04   # only this study: data checks, models, tables and final-reports/04-fund-selection.pdf
```

Runs without an API key, replaying recorded answers. Set `ANTHROPIC_API_KEY` to call Claude live.

## Question
An investment committee must choose which funds to offer on a menu (a company savings plan, a platform shortlist).
Two questions decide the rule: do last year's winners keep winning, and do cheaper funds leave investors better off?

## Result
- Last year's best fifth of equity funds beat the worst fifth by 1.11 points the following year, with a standard error of 4.61: no usable signal.
- The slope of next-year on this-year excess return is 0.094 for equity and 0.182 for fixed income, both significant but small.
- In fixed income, 39.3% of the best quintile stays best the next year, against 20% by chance; in equity, 28.0%.
- Each extra point of expense ratio goes with 0.735 points less net excess return in equity and 0.380 in multi-asset, both significant at 1%; in fixed income the slope is 0.061 and not significant.
- The cheapest third of equity funds (median expense ratio 0.16%) returned -4.99 points over the CDI the next year, against -7.18 for the most expensive third (median 2.82%).
- Over 10 years, the median equity investor who picks from the cheapest third ends with 0.72 of what the CDI would have given, against 0.69 for a random pick and 0.66 for last year's best quintile.
- Picking from the cheapest third and skipping last year's worst quintile gives the best median in every class: 0.74 in equity, 0.88 in multi-asset and 0.96 in fixed income.

Reading: past returns barely help; fees do. A menu rule of "cheapest third within each class, minus last year's
worst" beats picking at random or chasing winners, but in 2021-2025 even that trailed the CDI. Four year pairs is a short
history: these are associations in one period, not a law.

## More
- [How it was built](method.md): data, data checks, every modelling step and why.
- [Final report (PDF)](../../final-reports/04-fund-selection.pdf) · [AI review of this page](output/review.md)
- [Committee memo written by the AI](output/committee_memo.md)

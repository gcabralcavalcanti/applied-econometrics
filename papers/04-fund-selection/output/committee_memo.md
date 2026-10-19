# Memo to the investment committee: picking funds for a retail menu

*Written by Claude Haiku 5.5 from the tables in this folder; every number was checked by Python against the cells it cites, then the findings went through the reviewer. Not investment advice.*

**Recommendation.** Use fund fees as a screen: avoid funds in the most expensive third for equity and multi-asset menus, and do not select funds on last year's excess return alone, since past winners have not reliably repeated.

## Findings

1. In equity funds, each extra percentage point of annual expense ratio is associated with about 0.74 points less excess return the next year, and this is statistically significant.  
   *Source: tab_costs / Expense ratio (slope) / Equity; tab_costs / Expense ratio (slope) (std. error) / Equity. Reviewer: numbers and reading OK*
2. Equity funds in the cheapest third returned about -5.0 points a year versus the CDI next year, against about -7.2 points in the most expensive third; all equity groups lagged the CDI, but the cheap group lagged least.  
   *Source: tab_costs / Cheapest third: next-year excess / Equity; tab_costs / Most expensive third: next-year excess / Equity; tab_costs / Cheapest third: median expense ratio / Equity; tab_costs / Most expensive third: median expense ratio / Equity. Reviewer: numbers and reading OK*
3. Over 10 years, a random equity fund ends at a median of 0.69 times the CDI wealth and beats the CDI 27% of the time; picking the cheapest third raises this only slightly to 0.72 and 30%.  
   *Source: tab_montecarlo / Equity: Random fund / Median; tab_montecarlo / Equity: Random fund / Beats CDI (%); tab_montecarlo / Equity: Cheapest third / Median; tab_montecarlo / Equity: Cheapest third / Beats CDI (%). Reviewer: numbers and reading OK*
4. Past performance is a weak guide. Among equity funds, last year's best quintile went on to return -2.23 points versus the CDI next year, close to the worst quintile's -3.34; the best-minus-worst gap of 1.11 is far inside its error range.  
   *Source: tab_persistence / Q5 (best this year) / Equity; tab_persistence / Q1 (worst this year) / Equity; tab_persistence / Q5 minus Q1 / Equity; tab_persistence / Q5 minus Q1 (std. error) / Equity. Reviewer: numbers and reading OK*
5. Persistence is somewhat better in fixed income, where the best group this year is more likely to stay best (39.3%, against a 20% chance), but even there the best-minus-worst next-year gap is only 0.14 points with a large error, and fixed income funds rarely beat the CDI over 10 years (14% for a random fund).  
   *Source: tab_transition / Best quintile stays best (%) / Fixed income; tab_persistence / Q5 minus Q1 / Fixed income; tab_persistence / Q5 minus Q1 (std. error) / Equity; tab_montecarlo / Fixed income: Random fund / Beats CDI (%). Reviewer: numbers and reading OK*
6. Fees do not explain multi-asset returns much (R-squared 0.019), and expense ratio slopes are negative but smaller than in equity; cheapest-third multi-asset funds returned -1.72 points versus -2.59 for the most expensive third.  
   *Source: tab_costs / Expense ratio (slope) / Multi-asset; tab_costs / R^2 / Multi-asset; tab_costs / Cheapest third: next-year excess / Multi-asset; tab_costs / Most expensive third: next-year excess / Multi-asset. Reviewer: numbers and reading OK*

## Risks

- Results are associations over 2021-2025 and not causal effects; fees may correlate with other fund traits such as strategy or size that drive returns.
- Four year pairs is a short history, so the persistence and fee estimates could change materially with more years or a different market regime.
- Monte Carlo results assume returns are drawn independently from the sample and ignore fund closures and manager changes, which are only partly captured.
- Most fund groups lagged the CDI on average over this period, so conclusions about relative ranking may not transfer to a different rate environment.

## Next steps

- Set a fee cap for equity and multi-asset menu options, targeting funds outside the most expensive third, and document the rule.
- Stop using last year's excess return as the main selection criterion; review funds on fees, strategy fit and longer track records instead.
- Re-run this analysis with additional years of data before revisiting any performance-based selection rule.

# Reviewer report: 01-phillips-curve

Each statement of the README *Result* section, checked against the paper's tables.

| # | Statement | Numbers | Interpretation | Note |
|---|---|---|---|---|
| S1 | In the static model the unemployment coefficient is -0.002 (SE 0.010), with no stars: no static trade-off. | -0.002 → match; 0.010 → match | ok | F46 gives -0.002 and F48 gives SE (0.010) with no stars, so the static slope is insignificant. |
| S2 | In the dynamic model, lagged inflation has a coefficient of 0.398 and the Focus expectation 0.686, both significant at 1%; unemployment stays insignificant at 0.007. | 0.398 → match; 0.686 → match; 0.007 → match | ok | F50 and F52 are 0.398*** and 0.686***, significant at 1%; F47 gives unemployment 0.007 with SE 0.008, insignificant. |
| S3 | R² rises from 0.000 to 0.421, on 169 monthly observations. | 0.000 → match; 0.421 → match; 169 → match | ok | F66 gives static R² 0.000, F67 dynamic R² 0.421, and F65 gives 169 observations for the dynamic model. |
| S4 | H0: γ + δ = 1 is not rejected (p = 0.432): the data do not reject a vertical long-run Phillips curve. | 0.432 → match | ok | F63 reports p = 0.432 for H0: γ+δ=1, which fails to reject; the statement's wording that the data do not reject is appropriate, though a vertical curve is only one reading of a unit-sum restriction. |
| S5 | With Newey–West errors the standard error on the expectation term rises from 0.111 to 0.177; it stays significant. | 0.111 → match; 0.177 → match | ok | F32 is the usual SE 0.111 and F33 the HAC SE 0.177; the HAC coefficient stays 0.686*** (F31), so significance holds. |
| S6 | With seasonal dummies the expectation coefficient is 0.783 and R² 0.523; without the COVID months unemployment is 0.001. | 0.783 → match; 0.523 → match; 0.001 → match | ok | F101 gives expectation 0.783 with seasonal dummies, F119 gives R² 0.523, and F86 gives unemployment 0.001 in the no-COVID sample. |

## Flags and the author's answer

No flags.

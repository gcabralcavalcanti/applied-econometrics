# Reviewer report: 02-crime-panel

Each statement of the README *Result* section, checked against the paper's tables.

| # | Statement | Numbers | Interpretation | Note |
|---|---|---|---|---|
| S1 | Specification: Pooled OLS; log P(arrest): -0.633; log police per capita: 0.352 | -0.633 → match; 0.352 → match | ok | Pooled OLS table shows log P(arrest) coefficient -0.633 (F134) and log police per capita 0.352 (F142). |
| S2 | Specification: County fixed effects; log P(arrest): -0.395; log police per capita: 0.422 | -0.395 → match; 0.422 → match | ok | County fixed effects column shows -0.395 for log P(arrest) (F105) and 0.422 for police (F121). |
| S3 | Specification: Two-way fixed effects; log P(arrest): -0.360; log police per capita: 0.422 | -0.360 → match; 0.422 → match | ok | Two-way FE column shows -0.360 for log P(arrest) (F81) and 0.422 for police (F97). |
| S4 | Breusch–Pagan LM = 191.60 and White LM = 410.04, both with p < 0.0001: heteroskedasticity is clear. | 191.60 → match; 410.04 → match; 0.0001 → match | ok | Breusch-Pagan LM 191.60 (F128) and White LM 410.04 (F131), both p<0.0001 (F130, F133), supporting heteroskedasticity. |
| S5 | In the two-way model, clustering by county raises the standard error on the arrest elasticity from 0.033 to 0.064. | 0.033 → match; 0.064 → match | ok | Table shows conventional SE 0.033 (F3) and clustered SE 0.064 (F4) for log P(arrest) in the two-way model. |
| S6 | On police per capita the clustered standard error is 0.093, against 0.027 before. | 0.093 → match; 0.027 → match | ok | Clustered SE for police is 0.093 (F20) and conventional SE 0.027 (F19) in the two-way table. |

## Flags and the author's answer

No flags.

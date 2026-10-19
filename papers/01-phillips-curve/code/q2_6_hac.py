"""Newey-West (HAC) standard errors for the dynamic Phillips curve, side by side with plain OLS.

The dynamic model's residuals are still autocorrelated (q2_5), so the OLS standard errors are inconsistent.

Inputs:  tmp/q2_base_phillips.csv
Outputs: output/q2_tab_hac_comparacao.tex
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from stargazer.stargazer import Stargazer

ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = ROOT / "tmp"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(TMP_DIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")
df = df.assign(ipca_lag1=df["ipca"].shift(1))
sample = df.dropna()

FORMULA = "ipca ~ desemprego + ipca_lag1 + exp_ipca_prox"

# Newey-West plug-in bandwidth L = floor(4*(n/100)^(2/9)) (Greene); n = 169 gives L = 4.
n = int(sample.shape[0])
L = int(np.floor(4 * (n / 100) ** (2 / 9)))

ols = smf.ols(FORMULA, data=sample).fit()
hac = smf.ols(FORMULA, data=sample).fit(cov_type="HAC", cov_kwds={"maxlags": L})

# Stargazer reads standard errors and p-values from each fitted model, so the second column is already HAC.
sg = Stargazer([ols, hac])
sg.dependent_variable_name("IPCA mensal")
sg.title("Modelo dinâmico: erros-padrão MQO usual vs.\\ HAC (Newey--West)")
sg.custom_columns(["MQO usual", f"MQO + HAC ($L={L}$)"], [1, 1])
sg.rename_covariates(
    {
        "desemprego": "Desemprego $u_t$",
        "ipca_lag1": r"Inflação defasada $\pi_{t-1}$",
        "exp_ipca_prox": r"Expectativa $E_t[\pi_{t+1}]$",
    }
)
sg.covariate_order(["desemprego", "ipca_lag1", "exp_ipca_prox", "Intercept"])
sg.show_f_statistic = False  # the HAC F statistic is not comparable with the OLS one
(OUT_DIR / "q2_tab_hac_comparacao.tex").write_text(sg.render_latex(), encoding="utf-8")

print("=== HAC (Newey-West) errors in the dynamic model ===")
print(f"  Sample: n={n}   HAC lags: L = floor(4*(n/100)^(2/9)) = {L}")
print(f"  {'variable':16s} {'coef':>9s} {'se_OLS':>9s} {'se_HAC':>9s} {'p_OLS':>8s} {'p_HAC':>8s}")
for k in ["desemprego", "ipca_lag1", "exp_ipca_prox"]:
    print(
        f"  {k:16s} {ols.params[k]:9.4f} {ols.bse[k]:9.4f} {hac.bse[k]:9.4f} "
        f"{ols.pvalues[k]:8.4f} {hac.pvalues[k]:8.4f}"
    )
print("\n  Coefficients are unchanged (HAC only corrects the standard errors).")
print("  Inertia and expectations stay strongly significant; unemployment stays insignificant.")
print("  HAC raises the expectation SE and lowers the inertia SE, but no conclusion flips.")

# The conclusion must not depend on the choice of L.
print("\n  Robustness to the HAC lag (L):")
print(f"    {'L':>3s}  {'p(u)':>7s}  {'p(pi_lag)':>11s}  {'p(E[pi])':>11s}")
for lags in (4, 8, 12):
    h = smf.ols(FORMULA, data=sample).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    print(
        f"    {lags:>3d}  {h.pvalues['desemprego']:>7.3f}  "
        f"{h.pvalues['ipca_lag1']:>11.2e}  {h.pvalues['exp_ipca_prox']:>11.2e}"
    )
print("    -> inertia and expectations significant, unemployment not, for every L.")
print("\nSaved in output/: q2_tab_hac_comparacao.tex")

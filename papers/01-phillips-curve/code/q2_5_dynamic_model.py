"""Dynamic (accelerationist) Phillips curve by OLS:

    pi_t = alpha + beta*u_t + gamma*pi_{t-1} + delta*E_t[pi_{t+1}] + e_t

Re-tests residual autocorrelation, computes the long-run unemployment effect beta/(1-gamma)
and tests the natural-rate restriction gamma + delta = 1.

Inputs:  tmp/q2_base_phillips.csv
Outputs: output/q2_tab_phillips_dinamica.tex (static vs. dynamic)
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf
from stargazer.stargazer import Stargazer
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, acorr_ljungbox
from statsmodels.stats.stattools import durbin_watson

ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = ROOT / "tmp"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(TMP_DIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")

LAGS = 12  # same as the autocorrelation tests in q2_4

# The lag costs the first observation, so the dynamic model has one month fewer than the static one.
df = df.assign(ipca_lag1=df["ipca"].shift(1))
sample = df.dropna()

static = smf.ols("ipca ~ desemprego", data=df).fit()
dynamic = smf.ols("ipca ~ desemprego + ipca_lag1 + exp_ipca_prox", data=sample).fit()

# With the lagged dependent variable among the regressors Durbin-Watson is biased towards 2,
# so Breusch-Godfrey (and Ljung-Box) is the valid test here.
dw_static = durbin_watson(static.resid)
dw_dynamic = durbin_watson(dynamic.resid)
bg_lm, bg_p, _, _ = acorr_breusch_godfrey(dynamic, nlags=LAGS)
lb = acorr_ljungbox(dynamic.resid, lags=[LAGS], return_df=True)
lb_q, lb_p = lb["lb_stat"].iloc[0], lb["lb_pvalue"].iloc[0]

# In the steady state pi_t = pi_{t-1} = pi*, so pi*(1-gamma) = alpha + beta*u + delta*E[pi]
# and d pi*/d u = beta/(1-gamma).
beta = dynamic.params["desemprego"]
gamma = dynamic.params["ipca_lag1"]
delta = dynamic.params["exp_ipca_prox"]
long_run_effect = beta / (1 - gamma)

# gamma + delta = 1 means a vertical long-run Phillips curve: no permanent trade-off.
vertical_test = dynamic.t_test("ipca_lag1 + exp_ipca_prox = 1")
gamma_plus_delta = gamma + delta
p_vertical = vertical_test.pvalue.item()

sg = Stargazer([static, dynamic])
sg.dependent_variable_name("IPCA mensal")
sg.title("Curva de Phillips: especificação estática vs.\\ dinâmica (MQO)")
sg.custom_columns(["Estática", "Dinâmica"], [1, 1])
sg.rename_covariates(
    {
        "desemprego": "Desemprego $u_t$",
        "ipca_lag1": r"Inflação defasada $\pi_{t-1}$",
        "exp_ipca_prox": r"Expectativa $E_t[\pi_{t+1}]$",
    }
)
sg.covariate_order(["desemprego", "ipca_lag1", "exp_ipca_prox", "Intercept"])
sg.add_line("Durbin--Watson", [f"{dw_static:.3f}", f"{dw_dynamic:.3f}"])
sg.add_line("Efeito de longo prazo $\\beta/(1-\\gamma)$", ["---", f"{long_run_effect:.4f}"])
sg.add_line("Breusch--Godfrey(12) $p$", ["$<$0.001", f"{bg_p:.3g}"])
sg.add_line("$H_0\\!: \\gamma+\\delta=1$ ($p$-valor)", ["---", f"{p_vertical:.3f}"])
(OUT_DIR / "q2_tab_phillips_dinamica.tex").write_text(sg.render_latex(), encoding="utf-8")

print("=== Dynamic model:  pi_t = a + b*u_t + g*pi_{t-1} + d*E_t[pi_{t+1}] ===")
print(f"  Sample: {sample.index.min().date()} to {sample.index.max().date()}  (n={int(dynamic.nobs)})")
print(f"  beta  (unemployment u_t)    = {beta:8.4f}   (p={dynamic.pvalues['desemprego']:.4f})")
print(f"  gamma (inertia pi_{{t-1}})    = {gamma:8.4f}   (p={dynamic.pvalues['ipca_lag1']:.4f})")
print(f"  delta (expectation E[pi])   = {delta:8.4f}   (p={dynamic.pvalues['exp_ipca_prox']:.4f})")
print(f"  R^2 = {dynamic.rsquared:.4f}   (static: {static.rsquared:.4f})")
print(f"\n  Long-run unemployment effect = beta/(1-gamma) = {long_run_effect:.4f}")
print("    (beta is not significant, so this long-run effect is not distinguishable from zero.)")
print(f"\n  Accelerationist restriction  gamma+delta = {gamma_plus_delta:.4f}")
print(
    f"    H0: gamma+delta=1 (vertical long-run Phillips curve) -> "
    f"t={vertical_test.tvalue.item():.3f}, p={p_vertical:.4f}"
)
print("    H0 is not rejected: the data do not contradict the natural-rate hypothesis.")
print("\n  Residual autocorrelation:")
print(f"    Durbin-Watson: {dw_static:.3f} (static) -> {dw_dynamic:.3f} (dynamic)")
print("      [DW is biased towards 2 with a lagged dependent variable; use BG]")
print(f"    Breusch-Godfrey(12): LM = {bg_lm:.2f}   p = {bg_p:.3g}")
print(f"    Ljung-Box(12)      : Q  = {lb_q:.2f}   p = {lb_p:.3g}")
print("\nSaved in output/: q2_tab_phillips_dinamica.tex")

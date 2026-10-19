"""Heteroskedasticity in the pooled OLS: residual plots, Breusch-Pagan and White tests, HC1 errors.

Input:   tmp/q3_base_crime.csv
Outputs: output/q3_fig_residuos_scatter.*       squared residuals against regressors and fitted values
         output/q3_tab_heterocedasticidade.tex  Breusch-Pagan and White tests
         output/q3_tab_pooled_robusto.tex       conventional vs. HC1 robust standard errors
"""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan, het_white

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import q3_helpers as qh

ROOT = Path(__file__).resolve().parent.parent
TMPDIR = ROOT / "tmp"
OUTDIR = ROOT / "output"
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q3_base_crime.csv")
pooled = smf.ols("lcrmrte ~ " + " + ".join(qh.RHS_POOLED), data=base).fit()
u = pooled.resid.values
u2 = u**2
exog = pooled.model.exog
n = len(u)

# Breusch-Pagan: LM = n * R2 of the auxiliary regression of u^2 on the model's regressors
bp_lm, bp_p, _, _ = het_breuschpagan(u, exog)
bp_df = np.linalg.matrix_rank(exog) - 1
bp = {"stat": bp_lm, "df": int(bp_df), "p": bp_p}

# White by hand: levels, squares and cross products of every regressor (exog_i * exog_j, i <= j).
# Degrees of freedom come from the rank, because products of dummies are collinear;
# het_white is kept as a cross-check.
k = exog.shape[1]
x_white = np.column_stack([exog[:, i] * exog[:, j] for i in range(k) for j in range(i, k)])
rank_white = np.linalg.matrix_rank(x_white)
beta_white, *_ = np.linalg.lstsq(x_white, u2, rcond=None)
resid_white = u2 - x_white @ beta_white
r2_white = 1 - (resid_white @ resid_white) / (((u2 - u2.mean()) ** 2).sum())
white_lm = n * r2_white
white_df = int(rank_white - 1)
white_p = stats.chi2.sf(white_lm, white_df)
white = {"stat": white_lm, "df": white_df, "p": white_p}
white_sm = het_white(u, exog)

print(f"Breusch-Pagan: LM={bp_lm:.2f} df={bp_df} p={bp_p:.3g}")
print(
    f"White: LM={white_lm:.2f} df={white_df} p={white_p:.3g} "
    f"(het_white={white_sm[0]:.2f}, matches={abs(white_lm - white_sm[0]) < 0.5})"
)

qh.het_tests_table(
    OUTDIR / "q3_tab_heterocedasticidade.tex",
    bp,
    white,
    caption="Testes de heterocedasticidade no MQO agrupado",
    label="tab:q3_het",
)

qh.set_figure_style()
panels = [
    ("lprbarr", "ln(prob. prisão)"),
    ("lpolpc", "ln(polícia p.c.)"),
    ("ldensity", "ln(densidade)"),
    ("lpctymle", "ln(% jovens)"),
    ("lwcon", "ln(salário constr.)"),
    ("__fit__", "valor predito $\\hat{y}$"),
]
fig, axes = plt.subplots(2, 3, figsize=(9.2, 5.6))
fig.suptitle("Diagnóstico de heterocedasticidade: $\\hat{u}^2$ vs. regressores", y=0.99, fontsize=12.5)
for ax, (col, title) in zip(axes.ravel(), panels, strict=True):
    x = pooled.fittedvalues.values if col == "__fit__" else base[col].values
    ax.scatter(x, u2, s=9, color=qh.COLORS["blue"], alpha=0.40, edgecolor="none")
    ax.set_title(title, fontsize=9.5)
    ax.set_ylabel("$\\hat{u}^2$", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 0.96))
qh.add_source_note(fig)
fig.savefig(OUTDIR / "q3_fig_residuos_scatter.pdf")
fig.savefig(OUTDIR / "q3_fig_residuos_scatter.png", dpi=150)
plt.close(fig)

pooled_hc1 = smf.ols("lcrmrte ~ " + " + ".join(qh.RHS_POOLED), data=base).fit(cov_type="HC1")
footer = [
    (r"Controles + \textit{dummies}", ["Sim", "Sim"]),
    ("Erros-padrao", ["Convencional", "Robusto (HC1)"]),
]
qh.regression_table(
    OUTDIR / "q3_tab_pooled_robusto.tex",
    [("MQO usual", qh.extract(pooled)), ("MQO + HC1", qh.extract(pooled_hc1))],
    [(v, qh.LABELS[v]) for v in qh.DETERRENCE],
    footer,
    caption="MQO agrupado: erros convencionais vs.\\ robustos de White (HC1)",
    label="tab:q3_robusto",
)

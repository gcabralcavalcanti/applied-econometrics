"""Pooled OLS in logs: ln(crmrte) = a + b1 ln(prbarr) + b2 ln(polpc) + controls + u.

Input:   tmp/q3_base_crime.csv
Outputs: tmp/q3_pooled_resid.csv        residuals and fitted values
         output/q3_tab_pooled.tex
         output/q3_fig_dispersao.*      log crime against arrest probability and police per capita
"""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import q3_helpers as qh

ROOT = Path(__file__).resolve().parent.parent
TMPDIR = ROOT / "tmp"
OUTDIR = ROOT / "output"
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q3_base_crime.csv")

formula = "lcrmrte ~ " + " + ".join(qh.RHS_POOLED)
pooled = smf.ols(formula, data=base).fit()

print(
    f"Pooled: N={int(pooled.nobs)}, R2={pooled.rsquared:.4f}, "
    f"b1(prbarr)={pooled.params['lprbarr']:+.4f}, b2(polpc)={pooled.params['lpolpc']:+.4f}"
)

resid = base[["county", "year"] + qh.RHS_POOLED].copy()
resid["fitted"] = pooled.fittedvalues
resid["resid"] = pooled.resid
resid["resid2"] = pooled.resid**2
resid.to_csv(TMPDIR / "q3_pooled_resid.csv", index=False)

footer = [
    (r"Controles socioecon\^omicos", ["Sim"]),
    (r"\textit{Dummies} de regi\~ao", ["Sim"]),
    (r"Efeitos fixos de condado", [r"N\~ao"]),
    (r"Efeitos fixos de ano", [r"N\~ao"]),
    ("Erros-padrao", ["Convencional"]),
]
qh.regression_table(
    OUTDIR / "q3_tab_pooled.tex",
    [("MQO agrupado", qh.extract(pooled))],
    [(v, qh.LABELS[v]) for v in qh.DETERRENCE],
    footer,
    caption="MQO agrupado (\\textit{pooled}) em logaritmos",
    label="tab:q3_pooled",
)

qh.set_figure_style()
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6))
fig.suptitle("Dispersão: crime e dissuasão (todas as obs., em logs)", y=0.99, fontsize=12.5)
pairs = [
    ("lprbarr", "ln(prob. de prisão)", qh.COLORS["red"]),
    ("lpolpc", "ln(polícia per capita)", qh.COLORS["green"]),
]
for ax, (x, xlabel, color) in zip(axes, pairs, strict=True):
    ax.scatter(base[x], base["lcrmrte"], s=10, color=color, alpha=0.45, edgecolor="none")
    b1, b0 = np.polyfit(base[x], base["lcrmrte"], 1)
    xs = np.linspace(base[x].min(), base[x].max(), 50)
    ax.plot(xs, b0 + b1 * xs, color="0.20", lw=1.4)
    ax.set_title(f"incl. simples: {qh.fmt_num(b1, 2)}", fontsize=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("ln(taxa de crime)")
fig.tight_layout(rect=(0, 0.05, 1, 0.96))
qh.add_source_note(fig)
fig.savefig(OUTDIR / "q3_fig_dispersao.pdf")
fig.savefig(OUTDIR / "q3_fig_dispersao.png", dpi=150)
plt.close(fig)

"""Plot the three series and estimate the static Phillips curve by OLS: pi_t = alpha + beta*u_t + e_t.

Inputs:  tmp/q2_base_phillips.csv
Outputs: output/q2_fig_series.pdf, output/q2_fig_phillips_scatter.pdf, output/q2_tab_phillips_estatica.tex
"""

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from matplotlib.ticker import FuncFormatter
from stargazer.stargazer import Stargazer
from statsmodels.stats.stattools import durbin_watson

ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = ROOT / "tmp"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(TMP_DIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")

# Serif fonts to match the LaTeX document; decimal comma because the paper is in Portuguese.
plt.rcParams.update(
    {
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "axes.titlesize": 12,
        "axes.labelsize": 10.5,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9.5,
        "axes.grid": True,
        "grid.color": "0.85",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
    }
)
COLORS = {"ipca": "#1f4e79", "unemp": "#9c2b2b", "exp": "#2e6f3e"}
BCB_SOURCE = "Fonte: BCB — SGS (IPCA 433; desocupação PNADC 24369) e Expectativas/Focus. Elaboração própria."


def _decimal_comma(decimals):
    return FuncFormatter(lambda x, _: f"{x:.{decimals}f}".replace(".", ","))


def _source_note(figure, text):
    figure.text(0.012, 0.008, text, ha="left", va="bottom", fontsize=7.2, color="0.35", style="italic")


# One panel per series: the scales differ too much for a shared axis.
fig, axes = plt.subplots(3, 1, figsize=(7.4, 6.2), sharex=True)
fig.suptitle("Curva de Phillips brasileira — séries mensais (2012–2026)", y=0.975, fontsize=12.5)
panels = [
    ("ipca", "IPCA\n(% a.m.)", COLORS["ipca"]),
    ("desemprego", "Desemprego\nPNADC (%)", COLORS["unemp"]),
    ("exp_ipca_prox", "Expectativa\nFocus $E_t[\\pi_{t+1}]$ (%)", COLORS["exp"]),
]
for ax, (col, label, color) in zip(axes, panels, strict=True):
    ax.plot(df.index, df[col], color=color, lw=1.3)
    ax.set_ylabel(label, fontsize=9.5)
    ax.yaxis.set_major_formatter(_decimal_comma(1))
    ax.margins(x=0.01)
axes[-1].set_xlabel("Mês")
fig.subplots_adjust(left=0.135, right=0.985, top=0.93, bottom=0.085, hspace=0.12)
_source_note(fig, BCB_SOURCE)
fig.savefig(OUT_DIR / "q2_fig_series.pdf")
plt.close(fig)

model = smf.ols("ipca ~ desemprego", data=df).fit()
dw = durbin_watson(model.resid)
beta = model.params["desemprego"]
pval = model.pvalues["desemprego"]

fig2, ax = plt.subplots(figsize=(7.4, 5.0))
ax.scatter(df["desemprego"], df["ipca"], s=26, alpha=0.55, color=COLORS["ipca"], edgecolor="white", linewidth=0.4)
xs = df["desemprego"].sort_values()
alpha0 = model.params["Intercept"]
sign = "−" if beta < 0 else "+"  # avoids "+ -0,0024" in the legend
fit_label = f"MQO: $\\pi = {alpha0:.3f}".replace(".", ",") + f" {sign} {abs(beta):.4f}".replace(".", ",") + "\\,u$"
ax.plot(xs, alpha0 + beta * xs, color=COLORS["unemp"], lw=2.2, label=fit_label)
ax.set_xlabel("Taxa de desemprego (%)")
ax.set_ylabel("IPCA (% a.m.)")
ax.set_title("Curva de Phillips estática: inflação × desemprego (2012–2026)")
ax.xaxis.set_major_formatter(_decimal_comma(0))
ax.yaxis.set_major_formatter(_decimal_comma(1))
ax.legend(loc="upper left", frameon=True, framealpha=0.9)
ax.annotate(
    f"$R^2 \\approx {model.rsquared:.3f}$".replace(".", ",") + f";  $p_\\beta = {pval:.2f}$".replace(".", ","),
    xy=(0.985, 0.04),
    xycoords="axes fraction",
    ha="right",
    fontsize=9,
    color="0.3",
)
_source_note(fig2, BCB_SOURCE)
fig2.subplots_adjust(left=0.09, right=0.985, top=0.92, bottom=0.12)
fig2.savefig(OUT_DIR / "q2_fig_phillips_scatter.pdf")
plt.close(fig2)

# Covariate labels match the ones in q2_5 and q2_6.
sg = Stargazer([model])
sg.dependent_variable_name("IPCA mensal")
sg.title("Curva de Phillips estática — MQO: $\\pi_t = \\alpha + \\beta\\,u_t + \\varepsilon_t$")
sg.custom_columns(["IPCA mensal ($\\pi_t$)"], [1])
sg.rename_covariates({"desemprego": "Desemprego $u_t$"})
sg.covariate_order(["desemprego", "Intercept"])
sg.add_line("Durbin-Watson", [f"{dw:.3f}"])
with open(OUT_DIR / "q2_tab_phillips_estatica.tex", "w", encoding="utf-8") as f:
    f.write(sg.render_latex())

print("=== Static Phillips curve:  pi_t = alpha + beta*u_t + e_t ===")
print(f"  Sample: {df.index.min().date()} to {df.index.max().date()}  (n={int(model.nobs)})")
print(f"  beta (unemployment) = {beta:.4f}   (p-value = {pval:.4f})")
print(f"  alpha (intercept)   = {model.params['Intercept']:.4f}")
print(f"  R^2 = {model.rsquared:.4f}    Durbin-Watson = {dw:.3f}")
if pval >= 0.10:
    reading = (
        f"{'negative' if beta < 0 else 'positive'} but not significant "
        f"(p={pval:.2f}, R2~0) -> no visible static trade-off"
    )
else:
    reading = (
        "negative and significant (the textbook trade-off)"
        if beta < 0
        else "positive and significant (against the simple trade-off)"
    )
print(f"  -> beta: {reading}")
print("\nSaved in output/: q2_fig_series.pdf, q2_fig_phillips_scatter.pdf, q2_tab_phillips_estatica.tex")

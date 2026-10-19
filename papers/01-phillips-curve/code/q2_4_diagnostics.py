"""Stationarity and residual-autocorrelation diagnostics for the static Phillips curve.

Stationarity: ADF and KPSS in levels, ADF in first differences, plus the static model in differences.
Autocorrelation of the static residuals: Durbin-Watson, Breusch-Godfrey, Ljung-Box and the residual ACF.

Inputs:  tmp/q2_base_phillips.csv
Outputs: output/q2_tab_estacionariedade.tex, output/q2_tab_autocorrelacao.tex, output/q2_fig_acf_residuos.pdf
"""

import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from matplotlib.ticker import FuncFormatter
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, acorr_ljungbox
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.stattools import acf, adfuller, kpss

ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = ROOT / "tmp"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(TMP_DIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")

plt.rcParams.update(
    {
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "axes.titlesize": 12,
        "axes.labelsize": 10.5,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.grid": True,
        "grid.color": "0.85",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
    }
)
ACF_COLOR = "#1f4e79"


def _decimal_comma(decimals):
    return FuncFormatter(lambda x, _: f"{x:.{decimals}f}".replace(".", ","))


def _source_note(figure, text):
    figure.text(0.012, 0.008, text, ha="left", va="bottom", fontsize=7.2, color="0.35", style="italic")


# 12 lags = one year of monthly data, so the tests also pick up annual seasonality.
LAGS = 12

LABELS = {
    "ipca": r"IPCA (\% a.m.)",
    "desemprego": r"Desemprego (\%)",
    "exp_ipca_prox": r"Expectativa $E_t[\pi_{t+1}]$ (\%)",
}


# ADF (H0: unit root) and KPSS (H0: stationary) have opposite nulls and low power,
# so a series is called stationary or not only when both agree.
def run_adf(series):
    stat, p_value, *_ = adfuller(series.dropna(), regression="c", autolag="AIC")
    return stat, p_value


def run_kpss(series):
    # KPSS warns when the p-value falls outside its lookup table (">0.10" or "<0.01"); that is expected here.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InterpolationWarning)
        stat, p_value, *_ = kpss(series.dropna(), regression="c", nlags="auto")
    return stat, p_value


def joint_reading(p_adf, p_kpss):
    stationary_adf = p_adf < 0.05
    stationary_kpss = p_kpss >= 0.05
    if stationary_adf and stationary_kpss:
        return "Estacionária"
    if (not stationary_adf) and (not stationary_kpss):
        return "Não-estacionária"
    return "Persistente (evid.\\ mista)"


def fmt_kpss_p(p):
    # statsmodels caps the KPSS p-value to [0.01, 0.10]; show the bound instead of a fake number.
    if p >= 0.10:
        return r"$>$0.10"
    if p <= 0.01:
        return r"$<$0.01"
    return f"{p:.3f}"


adf_level = {c: run_adf(df[c]) for c in LABELS}
kpss_level = {c: run_kpss(df[c]) for c in LABELS}
adf_diff = {c: run_adf(df[c].diff()) for c in ["ipca", "desemprego"]}

static = smf.ols("ipca ~ desemprego", data=df).fit()
resid = static.resid

dw = durbin_watson(resid)
bg_lm, bg_p, _, _ = acorr_breusch_godfrey(static, nlags=LAGS)
lb = acorr_ljungbox(resid, lags=[LAGS], return_df=True)
lb_q, lb_p = lb["lb_stat"].iloc[0], lb["lb_pvalue"].iloc[0]

# The static model in first differences, only to illustrate the usual fix for spurious regression.
df_diff = df.assign(d_ipca=df["ipca"].diff(), d_desemprego=df["desemprego"].diff()).dropna()
static_diff = smf.ols("d_ipca ~ d_desemprego", data=df_diff).fit()

# Bartlett bands (alpha = 0.05), which widen with the lag.
ACF_NLAGS = 24
acf_vals, acf_ci = acf(resid, nlags=ACF_NLAGS, alpha=0.05, fft=False)
acf_lags = np.arange(ACF_NLAGS + 1)
band = acf_ci[:, 1] - acf_vals
fig, ax = plt.subplots(figsize=(7.4, 4.3))
ax.fill_between(acf_lags, -band, band, color=ACF_COLOR, alpha=0.13, lw=0)
ax.vlines(acf_lags, 0, acf_vals, color=ACF_COLOR, lw=1.4)
ax.scatter(acf_lags, acf_vals, s=22, color=ACF_COLOR, zorder=3)
ax.axhline(0, color="0.4", lw=0.8)
ax.set_title("FAC dos resíduos da Phillips estática")
ax.set_xlabel("Defasagem (meses)")
ax.set_ylabel("Autocorrelação")
ax.yaxis.set_major_formatter(_decimal_comma(2))
ax.set_xlim(-0.5, ACF_NLAGS + 0.5)
ax.set_ylim(-0.4, 1.02)
rho1 = acf_vals[1]
ax.annotate(
    f"$\\hat\\rho_1 \\approx {rho1:.3f}$".replace(".", ","),
    xy=(1, rho1),
    xytext=(3.2, 0.74),
    fontsize=9,
    color="0.25",
    arrowprops={"arrowstyle": "->", "color": "0.5", "lw": 0.9},
)
_source_note(fig, "Elaboração própria a partir dos resíduos da regressão estática.")
fig.subplots_adjust(left=0.10, right=0.985, top=0.90, bottom=0.135)
fig.savefig(OUT_DIR / "q2_fig_acf_residuos.pdf")
plt.close(fig)

rows = []
for col, label in LABELS.items():
    a_stat, a_p = adf_level[col]
    k_stat, k_p = kpss_level[col]
    rows.append(
        f"{label} & {a_stat:.2f} & {a_p:.3f} & {k_stat:.2f} & {fmt_kpss_p(k_p)} & {joint_reading(a_p, k_p)} \\\\"
    )
rows.append("\\midrule")
rows.append("\\multicolumn{6}{l}{\\textit{Em primeira diferença (apenas ADF):}} \\\\")
for col in ["ipca", "desemprego"]:
    a_stat, a_p = adf_diff[col]
    label = "$\\Delta$ " + LABELS[col]
    verdict = "Estacionária" if a_p < 0.05 else "Estac.\\ a 10\\%" if a_p < 0.10 else "Não-estac."
    rows.append(f"{label} & {a_stat:.2f} & {a_p:.3f} & --- & --- & {verdict} \\\\")

stationarity_tex = (
    "\\begin{table}[htbp]\n\\centering\n"
    "\\caption{Estacionariedade: ADF ($H_0$: raiz unitária) e KPSS "
    "($H_0$: estacionária)}\n\\label{tab:adf}\n"
    "\\begin{tabular}{lcccccc}\n\\toprule\n"
    "& \\multicolumn{2}{c}{ADF} & \\multicolumn{2}{c}{KPSS} & \\\\\n"
    "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n"
    "Série & Estat. & $p$ & Estat. & $p$ & Conclusão (5\\%) \\\\\n"
    "\\midrule\n" + "\n".join(rows) + "\n"
    "\\bottomrule\n\\end{tabular}\n\\end{table}\n"
)
(OUT_DIR / "q2_tab_estacionariedade.tex").write_text(stationarity_tex, encoding="utf-8")

autocorr_tex = (
    "\\begin{table}[htbp]\n\\centering\n"
    "\\caption{Autocorrelação dos resíduos da Phillips estática "
    "($H_0$: ausência de autocorrelação)}\n\\label{tab:autocorr}\n"
    "\\begin{tabular}{lccc}\n\\toprule\n"
    "Teste & Estatística & $p$-valor & Conclusão (5\\%) \\\\\n"
    "\\midrule\n"
    f"Durbin--Watson & {dw:.3f} & --- & Autocorrelação positiva \\\\\n"
    f"Breusch--Godfrey ({LAGS} defas.) & {bg_lm:.2f} & {bg_p:.3g} & Rejeita $H_0$ \\\\\n"
    f"Ljung--Box ({LAGS} defas.) & {lb_q:.2f} & {lb_p:.3g} & Rejeita $H_0$ \\\\\n"
    "\\bottomrule\n\\end{tabular}\n\\end{table}\n"
)
(OUT_DIR / "q2_tab_autocorrelacao.tex").write_text(autocorr_tex, encoding="utf-8")

print("=== Stationarity (ADF: H0 = unit root; KPSS: H0 = stationary) ===")
for col in LABELS:
    a_stat, a_p = adf_level[col]
    k_stat, k_p = kpss_level[col]
    kpss_p = ">0.10" if k_p >= 0.10 else f"{k_p:.3f}"
    print(
        f"  {col:14s} ADF={a_stat:7.3f} (p={a_p:.3f}) | KPSS={k_stat:.3f} (p={kpss_p})"
        f"  -> {joint_reading(a_p, k_p).replace(chr(92), '')}"
    )
print("  first difference (ADF):")
for col in ["ipca", "desemprego"]:
    a_stat, a_p = adf_diff[col]
    print(f"  d.{col:12s} ADF={a_stat:7.3f}  p={a_p:.3f}")
print(
    f"  Static model in differences: beta(d.desemprego) = {static_diff.params['d_desemprego']:.4f} "
    f"(p={static_diff.pvalues['d_desemprego']:.3f}), R2={static_diff.rsquared:.4f}"
)
print("  -> IPCA stationary in both tests; unemployment and expectations are persistent with")
print("     mixed evidence (ADF does not reject a unit root; KPSS does not reject stationarity).")

print("\n=== Autocorrelation of the static residuals (H0 = no autocorrelation) ===")
print(f"  Durbin-Watson           = {dw:.3f}   (~2 = none; <2 = positive)")
print(f"  Breusch-Godfrey({LAGS})    : LM = {bg_lm:.2f}   p = {bg_p:.3g}")
print(f"  Ljung-Box({LAGS})          : Q  = {lb_q:.2f}   p = {lb_p:.3g}")
print("  -> All three show strong autocorrelation: the static model is misspecified")
print("     (no inertia, no expectations), which motivates the dynamic model (q2_5).")
print("  The classic spurious-regression symptom (high R2 + low DW) does not appear:")
print("     R2 is ~0 because IPCA is I(0); the low DW reflects omitted dynamics,")
print("     not a trend regressed on a trend.")
print("\nSaved in output/: q2_tab_estacionariedade.tex, q2_tab_autocorrelacao.tex, q2_fig_acf_residuos.pdf")

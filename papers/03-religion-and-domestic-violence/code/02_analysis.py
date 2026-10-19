"""Estimate the models, the robustness checks, and write the tables and figures.

Models: OLS with HC1 errors, quadratic, log(1+y), non-domestic notification proxy, WLS by population,
Poisson with a population offset; all with state fixed effects.

Input:  tmp/base_corte_2011_2013.csv, tmp/base_corte_2013_2015.csv, tmp/controles.csv, tmp/sinan_mun_ano.csv
Output: output/tables/*.tex, output/tables/_stats.txt, output/figures/*.pdf and *.png
"""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_white

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tmp"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

STATE_CAPITALS = {
    "1200401", "2704302", "1600303", "1302603", "2927408", "2304400", "5300108", "3205309", "5208707",
    "2111300", "5103403", "5002704", "3106200", "1501402", "2507507", "4106902", "2611606", "2211001",
    "3304557", "2408102", "4314902", "1100205", "1400100", "4205407", "3550308", "2800308", "1721000",
}  # fmt: skip
BASE_FORMULA = "vd ~ evang + l_renda + l_pop + C(uf)"


def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def coef_cells(model, term):
    """(coefficient with stars, standard error in parentheses); blank if the term is not in the model."""
    if term not in model.params.index:
        return ("", "")
    return (f"{model.params[term]:.4f}{stars(model.pvalues[term])}", f"({model.bse[term]:.4f})")


def fit_ols(data, formula, weights=None, cluster=None):
    """OLS (or WLS if weights is a column name) with HC1 errors, or clustered by the given column."""
    if cluster:
        cov = dict(cov_type="cluster", cov_kwds={"groups": data[cluster]})
    else:
        cov = dict(cov_type="HC1")
    if weights:
        return smf.wls(formula, data, weights=data[weights]).fit(**cov)
    return smf.ols(formula, data).fit(**cov)


def binned_means(x, y, n_bins=20):
    bins = pd.qcut(x, n_bins, duplicates="drop")
    groups = pd.DataFrame({"x": x, "y": y, "q": bins}).groupby("q", observed=True)
    return groups["x"].mean(), groups["y"].mean()


def window_base(first_year, last_year):
    """Rate per 1,000 residents over a window, merged with the controls (same definition as 01_build_base.py)."""
    window = sinan[(sinan.ano >= first_year) & (sinan.ano <= last_year)]
    base = (
        window.groupby("municipio_id")
        .agg(vf=("n_dom_s0", "sum"), an=("ano", "nunique"))
        .reset_index()
        .merge(controls, on="municipio_id", how="inner")
    )
    base["vd"] = base["vf"] / base["an"] / base["pop_total"] * 1000
    base["l_renda"] = np.log(base["renda_percapita"])
    base["l_pop"] = np.log(base["pop_total"])
    base["evang"] = base["evangelical_density"]
    return base


# Data
base = pd.read_csv(TMP / "base_corte_2011_2013.csv", dtype={"municipio_id": str})
base["uf"] = base["municipio_id"].str.zfill(7).str[:2]
base_2013 = pd.read_csv(TMP / "base_corte_2013_2015.csv", dtype={"municipio_id": str})
base_2013["uf"] = base_2013["municipio_id"].str.zfill(7).str[:2]
controls = pd.read_csv(TMP / "controles.csv", dtype={"municipio_id": str})
controls["municipio_id"] = controls["municipio_id"].str.zfill(7)
sinan = pd.read_csv(TMP / "sinan_mun_ano.csv", sep=";", dtype={"municipio_id": str})
sinan["municipio_id"] = sinan["municipio_id"].str.zfill(7)

# municipalities present in both windows, so the two windows compare the same sample
common = set(base.municipio_id) & set(base_2013.municipio_id)
base_common = base[base.municipio_id.isin(common)]
base_2013_common = base_2013[base_2013.municipio_id.isin(common)]

# Models
m1 = fit_ols(base, BASE_FORMULA)
m2 = fit_ols(base, "vd ~ evang + evang2c + l_renda + l_pop + C(uf)")
m3 = fit_ols(base, "lvd ~ evang + l_renda + l_pop + C(uf)")
m4 = fit_ols(base, "vd ~ evang + l_renda + l_pop + notif_nondom + C(uf)")
m5 = fit_ols(base, BASE_FORMULA, weights="pop_total")
poisson = smf.glm(
    "vd_count ~ evang + l_renda + l_pop + C(uf)",
    base,
    family=sm.families.Poisson(),
    offset=np.log(base["pop_total"]),
).fit(cov_type="HC1")

white_lm, white_p, _, _ = het_white(m1.resid, m1.model.exog)
k = int(m1.df_model)
zeros_pct = (base["vd"] == 0).mean() * 100
sinan_window = sinan[(sinan.ano >= 2011) & (sinan.ano <= 2013)]
domestic_share = sinan_window["n_dom_s0"].sum() / sinan_window["n_total"].sum() * 100

# Descriptive statistics
descriptive_labels = [
    ("vd", "Taxa de VD doméstica feminina (por mil hab.)"),
    ("evang", "Densidade evangélica (\\%)"),
    ("renda_percapita", "Renda per capita (R\\$)"),
    ("pop_total", "População"),
    ("notif_nondom", "Notificações não-domésticas (por mil)"),
]
with open(TABLES / "tab_descritivas.tex", "w", encoding="utf-8") as f:
    f.write("\\begin{tabular}{lrrrrrr}\n\\toprule\nVariável & N & Média & DP & Mín & Mediana & Máx \\\\\n\\midrule\n")
    for var, label in descriptive_labels:
        s = base[var]
        f.write(
            f"{label} & {int(s.count())} & {s.mean():,.2f} & {s.std():,.2f} & {s.min():,.2f} "
            f"& {s.median():,.2f} & {s.max():,.2f} \\\\\n"
        )
    f.write("\\bottomrule\n\\end{tabular}\n")

# Main table
main_models = [("(1)", m1), ("(2)", m2), ("(3)", m3), ("(4)", m4), ("(5)", m5)]
main_terms = [
    ("evang", "Densidade evangélica"),
    ("evang2c", "Densidade evangélica$^2$/100"),
    ("l_renda", "log(Renda pc)"),
    ("l_pop", "log(População)"),
    ("notif_nondom", "Notif. não-domésticas"),
]
with open(TABLES / "tab_principal.tex", "w", encoding="utf-8") as f:
    f.write(
        "\\begin{tabular}{lccccc}\n\\toprule\n& (1) & (2) & (3) & (4) & (5) \\\\\n"
        "Dependente & VD & VD & log(1+VD) & VD & VD \\\\\nEstimador & MQO & MQO & MQO & MQO & WLS \\\\\n\\midrule\n"
    )
    for term, label in main_terms:
        cells = [coef_cells(m, term) for _, m in main_models]
        f.write(label + "".join(" & " + c[0] for c in cells) + " \\\\\n")
        f.write("".join(" & " + c[1] for c in cells) + " \\\\\n")
    f.write("\\midrule\nEfeitos fixos de UF" + " & Sim" * 5 + " \\\\\n")
    f.write("Observações" + "".join(f" & {int(m.nobs)}" for _, m in main_models) + " \\\\\n")
    f.write("$R^2$" + "".join(f" & {m.rsquared:.3f}" for _, m in main_models) + " \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")

# Robustness
robustness = [
    ("Base 2011–13", fit_ols(base, BASE_FORMULA)),
    ("2011–13 (comum)", fit_ols(base_common, BASE_FORMULA)),
    ("2013–15 (comum)", fit_ols(base_2013_common, BASE_FORMULA)),
    ("Sem capitais", fit_ols(base[~base.municipio_id.isin(STATE_CAPITALS)], BASE_FORMULA)),
    ("Cluster UF", fit_ols(base, BASE_FORMULA, cluster="uf")),
    ("Pop. $\\geq$ 5k", fit_ols(base[base.pop_total >= 5000], BASE_FORMULA)),
]
with open(TABLES / "tab_robustez.tex", "w", encoding="utf-8") as f:
    f.write("\\begin{tabular}{l" + "c" * len(robustness) + "}\n\\toprule\n& ")
    f.write(" & ".join(name for name, _ in robustness) + " \\\\\n\\midrule\n")
    f.write("Densidade evangélica" + "".join(" & " + coef_cells(m, "evang")[0] for _, m in robustness) + " \\\\\n")
    f.write("".join(" & " + coef_cells(m, "evang")[1] for _, m in robustness) + " \\\\\n")
    f.write("\\midrule\nControles+EF UF" + " & Sim" * len(robustness) + " \\\\\n")
    f.write("Observações" + "".join(f" & {int(m.nobs)}" for _, m in robustness) + " \\\\\n")
    f.write("$R^2$" + "".join(f" & {m.rsquared:.3f}" for _, m in robustness) + " \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")

# Poisson
with open(TABLES / "tab_poisson.tex", "w", encoding="utf-8") as f:
    f.write("\\begin{tabular}{lcc}\n\\toprule\n& Coef. & IRR \\\\\n\\midrule\n")
    for term, label in [("evang", "Densidade evangélica"), ("l_renda", "log(Renda pc)")]:
        coef = poisson.params[term]
        f.write(f"{label} & {coef:.4f}{stars(poisson.pvalues[term])} & {np.exp(coef):.4f} \\\\\n")
        f.write(f" & ({poisson.bse[term]:.4f}) & \\\\\n")
    f.write(
        "\\midrule\nOffset log(pop.) & Sim & \\\\\nEF de UF & Sim & \\\\\n"
        f"Observações & {int(poisson.nobs)} & \\\\\n\\bottomrule\n\\end{{tabular}}\n"
    )

# Numbers quoted in the text
second_window = robustness[2][1]
stats = {
    "share_vd_total": f"{domestic_share:.1f}",
    "zeros_pct": f"{zeros_pct:.1f}",
    "White_LM": f"{white_lm:.1f}",
    "White_gl": f"{k}",
    "White_p": f"{white_p:.2g}",
    "F": f"{m1.fvalue:.1f}",
    "Fgl": f"({k},{int(m1.df_resid)})",
    "N_base": f"{int(m1.nobs)}",
    "R2_M1": f"{m1.rsquared:.3f}",
    "R2_M4": f"{m4.rsquared:.3f}",
    "proxy_b": f"{m4.params['notif_nondom']:.4f}",
    "proxy_p": f"{m4.pvalues['notif_nondom']:.2g}",
    "evang_M1": f"{m1.params['evang']:.4f}",
    "evang_M1_p": f"{m1.pvalues['evang']:.3g}",
    "evang_2013": f"{second_window.params['evang']:.4f}",
    "evang_2013_p": f"{second_window.pvalues['evang']:.3g}",
    "common": f"{len(common)}",
}
with open(TABLES / "_stats.txt", "w", encoding="utf-8") as f:
    f.write("".join(f"{key}={value}\n" for key, value in stats.items()))

# Binned scatter plots with the OLS line
plt.rcParams.update({"font.size": 11, "figure.dpi": 120})
scatter_specs = [
    ("evang", "Densidade evangélica (%)", "fig_evang_vd"),
    ("notif_nondom", "Notificações não-domésticas (por mil)", "fig_proxy_vd"),
]
for x_var, x_label, file_name in scatter_specs:
    bin_x, bin_y = binned_means(base[x_var], base["vd"])
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.scatter(bin_x, bin_y, color="#3b6ea5", s=28)
    slope, intercept = np.polyfit(base[x_var], base["vd"], 1)
    grid = np.linspace(base[x_var].min(), base[x_var].max(), 50)
    ax.plot(grid, intercept + slope * grid, color="#c0392b", lw=1.6)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Taxa de VD doméstica (por mil)")
    fig.tight_layout()
    fig.savefig(FIGURES / f"{file_name}.pdf")
    fig.savefig(FIGURES / f"{file_name}.png")
    plt.close()

# Rolling 3-year windows
rolling = []
for start in range(2009, 2018):
    model = fit_ols(window_base(start, start + 2), BASE_FORMULA)
    rolling.append((f"{start}-{start + 2}", model.params["evang"], model.bse["evang"]))
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.errorbar(
    range(len(rolling)),
    [r[1] for r in rolling],
    yerr=[1.96 * r[2] for r in rolling],
    fmt="o",
    color="#3b6ea5",
    capsize=3,
)
ax.axhline(0, color="#c0392b", lw=1, ls="--")
ax.set_xticks(range(len(rolling)))
ax.set_xticklabels([r[0] for r in rolling], rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Coef. densidade evangélica")
ax.set_title("Coeficiente por janela móvel de 3 anos (IC 95%)")
fig.tight_layout()
fig.savefig(FIGURES / "fig_coef_janelas.pdf")
fig.savefig(FIGURES / "fig_coef_janelas.png")
plt.close()

print(
    f"[02] OK. N={int(m1.nobs)} R2_M1={m1.rsquared:.3f} R2_M4={m4.rsquared:.3f} "
    f"evang_M1={m1.params['evang']:+.4f}(p={m1.pvalues['evang']:.2g}) "
    f"zeros={zeros_pct:.1f}% share={domestic_share:.1f}%"
)

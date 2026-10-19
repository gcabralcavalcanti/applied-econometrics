"""Shared helpers for the crime-panel scripts.

Number formatting with a decimal comma, booktabs LaTeX tables built from statsmodels and linearmodels
results, figure style, and the model specification used by every script. Table and figure text is in
Portuguese, as graded.
"""

from pathlib import Path

import numpy as np

SOURCE = (
    "Fonte: Cornwell e Trumbull (1994), painel de 90 condados da Carolina do "
    "Norte (1981-1987), via wooldridge::crime4. Elaboracao propria."
)

COLORS = {"blue": "#1f4e79", "red": "#9c2b2b", "green": "#2e6f3e", "gray": "#555555", "orange": "#b5651d"}


def fmt_num(x, decimals=3):
    if x is None:
        return "--"
    try:
        if np.isnan(x):
            return "--"
    except TypeError:
        return "--"
    return f"{x:.{decimals}f}".replace(".", ",")


def stars(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def fmt_pval(p, decimals=4):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "--"
    floor = 10 ** (-decimals)
    if p < floor:
        return ("$<$" + f"{floor:.{decimals}f}").replace(".", ",")
    return fmt_num(p, decimals)


def extract(res):
    """Put statsmodels OLS and linearmodels PanelOLS results in the same shape."""
    if hasattr(res, "bse"):
        return {
            "coef": res.params,
            "se": res.bse,
            "p": res.pvalues,
            "n": int(res.nobs),
            "r2": float(getattr(res, "rsquared", np.nan)),
        }
    return {"coef": res.params, "se": res.std_errors, "p": res.pvalues, "n": int(res.nobs), "r2": float(res.rsquared)}


def _cell(ext, var, decimals):
    if var not in ext["coef"].index:
        return None
    b, s, p = ext["coef"][var], ext["se"][var], ext["p"][var]
    return fmt_num(b, decimals) + stars(p), "(" + fmt_num(s, decimals) + ")"


def _write(path, lines):
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def regression_table(
    path, models, var_labels, footer, caption, label, decimals=3, note=None, dep_var="ln(taxa de crime)"
):
    ncol = len(models)
    lines = [
        r"\begin{table}[htbp]\centering",
        rf"\caption{{{caption}}}\label{{{label}}}",
        r"\small",
        rf"\begin{{tabular}}{{l{'c' * ncol}}}",
        r"\toprule",
        " & " + " & ".join(rf"\textbf{{{t}}}" for t, _ in models) + r" \\",
        " & " + " & ".join(f"({i + 1})" for i in range(ncol)) + r" \\",
        r"\midrule",
    ]
    for var, var_label in var_labels:
        coef_row, se_row = [var_label], [""]
        for _, ext in models:
            cell = _cell(ext, var, decimals)
            coef_row.append(cell[0] if cell else "")
            se_row.append(cell[1] if cell else "")
        lines.append(" & ".join(coef_row) + r" \\")
        lines.append(" & ".join(se_row) + r" \\")
    lines.append(r"\midrule")
    for row_label, vals in footer:
        lines.append(row_label + " & " + " & ".join(str(v) for v in vals) + r" \\")
    lines.append("N (obs.) & " + " & ".join(str(ext["n"]) for _, ext in models) + r" \\")
    lines.append(r"$R^2$ & " + " & ".join(fmt_num(ext["r2"], 3) for _, ext in models) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    if note is None:
        note = f"Erros-padrao entre parenteses. *** p$<$0,01; ** p$<$0,05; * p$<$0,10. Variavel dependente: {dep_var}."
    lines.append(rf"\par\vspace{{2pt}}{{\footnotesize\itshape {note}}}")
    lines.append(r"\end{table}")
    _write(path, lines)


def descriptives_table(path, df, var_labels, caption, label, decimals=3):
    lines = [
        r"\begin{table}[htbp]\centering",
        rf"\caption{{{caption}}}\label{{{label}}}",
        r"\small",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Variavel & Obs. & Media & Desv.-padrao & Min. & Max. \\",
        r"\midrule",
    ]
    for var, var_label in var_labels:
        s = df[var]
        lines.append(
            f"{var_label} & {int(s.count())} & {fmt_num(s.mean(), decimals)} & "
            f"{fmt_num(s.std(), decimals)} & {fmt_num(s.min(), decimals)} & {fmt_num(s.max(), decimals)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        rf"\par\vspace{{2pt}}{{\footnotesize\itshape {SOURCE}}}",
        r"\end{table}",
    ]
    _write(path, lines)


def het_tests_table(path, bp, white, caption, label):
    lines = [
        r"\begin{table}[htbp]\centering",
        rf"\caption{{{caption}}}\label{{{label}}}",
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r"Teste & Estatistica LM & g.l. & p-valor \\",
        r"\midrule",
        rf"Breusch--Pagan & {fmt_num(bp['stat'], 2)} & {bp['df']} & {fmt_pval(bp['p'])} \\",
        rf"White & {fmt_num(white['stat'], 2)} & {white['df']} & {fmt_pval(white['p'])} \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\vspace{2pt}{\footnotesize\itshape $H_0$: homocedasticidade. "
        r"Estatistica LM $=n\cdot R^2$ da regressao auxiliar. Rejeitar $H_0$ "
        r"indica heterocedasticidade.}",
        r"\end{table}",
    ]
    _write(path, lines)


def set_figure_style():
    import matplotlib.pyplot as plt

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


def add_source_note(fig, text=SOURCE):
    fig.text(0.012, 0.008, text, ha="left", va="bottom", fontsize=7.0, color="0.35", style="italic")


# Model specification shared by every script
DETERRENCE = ["lprbarr", "lprbconv", "lprbpris", "lavgsen", "lpolpc"]
CONTINUOUS = DETERRENCE + ["ldensity", "lpctymle", "ltaxpc", "lmix", "lwcon", "pctmin80"]
DUMMIES = ["west", "central", "urban"]
RHS_POOLED = CONTINUOUS + DUMMIES
# Time-invariant controls (region, density, demographics) are absorbed by the county effects
RHS_FE = ["lprbarr", "lprbconv", "lprbpris", "lavgsen", "lpolpc", "ltaxpc", "lmix", "lwcon"]
LABELS = {
    "lprbarr": r"ln(prob.\ pris\~ao) $\beta_1$",
    "lpolpc": r"ln(pol\'icia p.c.) $\beta_2$",
    "lprbconv": r"ln(prob.\ condena\c{c}\~ao)",
    "lprbpris": r"ln(prob.\ encarc.)",
    "lavgsen": r"ln(senten\c{c}a m\'edia)",
}
DESCRIPTIVE_VARS = [
    ("crmrte", "Taxa de crime (crimes/pessoa)"),
    ("prbarr", "Prob.\\ de pris\\~ao"),
    ("prbconv", "Prob.\\ de condena\\c{c}\\~ao"),
    ("prbpris", "Prob.\\ de encarceramento"),
    ("avgsen", "Senten\\c{c}a m\\'edia (dias)"),
    ("polpc", "Pol\\'icia per capita"),
    ("density", "Densidade (hab./mi$^2$)"),
    ("taxpc", "Receita tribut\\'aria p.c."),
    ("pctymle", "\\% homens jovens"),
    ("pctmin80", "\\% minoria (1980)"),
    ("mix", "Raz\\~ao crimes graves/leves"),
]

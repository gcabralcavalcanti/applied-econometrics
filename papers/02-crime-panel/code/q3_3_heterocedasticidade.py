"""
q3_3 - diagnostico de heterocedasticidade do MQO agrupado: (a) painel de
dispersao de u^2 contra os regressores continuos e o predito (o "funil");
(b) testes de Breusch-Pagan e White; (c) reestima o pooled com erros-padrao
robustos de White (HC1) e compara com os convencionais.

Autor: Guilherme Cabral (Grupo 1)
Data: 27/06/2026
Inputs:  tmp/q3_base_crime.csv
Outputs: output/q3_fig_residuos_scatter.pdf
         output/q3_tab_heterocedasticidade.tex
         output/q3_tab_pooled_robusto.tex
"""
import importlib.util as _ilu
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan, het_white

_hp = Path(__file__).resolve().parent / ".q3_helpers.py"
_spec = _ilu.spec_from_file_location("q3_helpers", _hp)
H = _ilu.module_from_spec(_spec); _spec.loader.exec_module(H)

RAIZ = Path(__file__).resolve().parent.parent
TMPDIR = RAIZ / "tmp"; OUTDIR = RAIZ / "output"; OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q3_base_crime.csv")
pooled = smf.ols("lcrmrte ~ " + " + ".join(H.RHS_POOLED), data=base).fit()
u = pooled.resid.values
u2 = u ** 2
exog = pooled.model.exog
n = len(u)

# Breusch-Pagan: LM = n*R2 da auxiliar u^2 ~ regressores do modelo
bp_lm, bp_p, bp_f, bp_fp = het_breuschpagan(u, exog)
bp_df = np.linalg.matrix_rank(exog) - 1
bp = {"stat": bp_lm, "df": int(bp_df), "p": bp_p}

# White: auxiliar com niveis + quadrados + produtos cruzados de todos os
# regressores (produtos exog_i*exog_j, i<=j). g.l. pelo posto (robusto a
# colinearidade de dummies); confiro a igualdade com het_white.
k = exog.shape[1]
cols = [exog[:, i] * exog[:, j] for i in range(k) for j in range(i, k)]
Xw = np.column_stack(cols)
postoW = np.linalg.matrix_rank(Xw)
betaW, *_ = np.linalg.lstsq(Xw, u2, rcond=None)
resW = u2 - Xw @ betaW
R2w = 1 - (resW @ resW) / (((u2 - u2.mean()) ** 2).sum())
white_lm = n * R2w
white_df = int(postoW - 1)
white_p = stats.chi2.sf(white_lm, white_df)
white = {"stat": white_lm, "df": white_df, "p": white_p}
w_sm = het_white(u, exog)

print(f"Breusch-Pagan: LM={bp_lm:.2f} gl={bp_df} p={bp_p:.3g}")
print(f"White: LM={white_lm:.2f} gl={white_df} p={white_p:.3g} "
      f"(het_white={w_sm[0]:.2f}, bate={abs(white_lm - w_sm[0]) < 0.5})")

H.tabela_testes_het(
    OUTDIR / "q3_tab_heterocedasticidade.tex", bp, white,
    caption="Testes de heterocedasticidade no MQO agrupado",
    label="tab:q3_het")

# painel de dispersao de u^2 contra regressores continuos e o predito
H.estilo_figuras()
paineis = [("lprbarr", "ln(prob. prisão)"), ("lpolpc", "ln(polícia p.c.)"),
           ("ldensity", "ln(densidade)"), ("lpctymle", "ln(% jovens)"),
           ("lwcon", "ln(salário constr.)"), ("__fit__", "valor predito $\\hat{y}$")]
fig, axes = plt.subplots(2, 3, figsize=(9.2, 5.6))
fig.suptitle("Diagnóstico de heterocedasticidade: $\\hat{u}^2$ vs. regressores", y=0.99, fontsize=12.5)
for ax, (col, rot) in zip(axes.ravel(), paineis):
    x = pooled.fittedvalues.values if col == "__fit__" else base[col].values
    ax.scatter(x, u2, s=9, color=H.COR["azul"], alpha=0.40, edgecolor="none")
    ax.set_title(rot, fontsize=9.5)
    ax.set_ylabel("$\\hat{u}^2$", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 0.96))
H.nota_fonte(fig)
fig.savefig(OUTDIR / "q3_fig_residuos_scatter.pdf")
fig.savefig(OUTDIR / "q3_fig_residuos_scatter.png", dpi=150)
plt.close(fig)

# correcao com erros robustos de White (HC1) vs convencionais
pooled_hc1 = smf.ols("lcrmrte ~ " + " + ".join(H.RHS_POOLED), data=base).fit(cov_type="HC1")
rodape = [
    (r"Controles + \textit{dummies}", ["Sim", "Sim"]),
    ("Erros-padrao", ["Convencional", "Robusto (HC1)"]),
]
H.tabela_regressao(
    OUTDIR / "q3_tab_pooled_robusto.tex",
    [("MQO usual", H.extrai(pooled)), ("MQO + HC1", H.extrai(pooled_hc1))],
    [(v, H.ROT[v]) for v in H.DETERRENCIA], rodape,
    caption="MQO agrupado: erros convencionais vs.\\ robustos de White (HC1)",
    label="tab:q3_robusto")

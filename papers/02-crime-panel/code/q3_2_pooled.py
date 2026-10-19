"""
q3_2 - estima o MQO agrupado (pooled) em logaritmos:
ln(crmrte) = a + b1 ln(prbarr) + b2 ln(polpc) + controles + u. Guarda os residuos
e os preditos (para o diagnostico de heterocedasticidade do q3_3) e gera a tabela
do pooled e a figura de dispersao.

Autor: Guilherme Cabral (Grupo 1)
Data: 27/06/2026
Inputs:  tmp/q3_base_crime.csv
Outputs: tmp/q3_pooled_resid.csv
         output/q3_tab_pooled.tex
         output/q3_fig_dispersao.pdf
"""
import importlib.util as _ilu
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

_hp = Path(__file__).resolve().parent / ".q3_helpers.py"
_spec = _ilu.spec_from_file_location("q3_helpers", _hp)
H = _ilu.module_from_spec(_spec); _spec.loader.exec_module(H)

RAIZ = Path(__file__).resolve().parent.parent
TMPDIR = RAIZ / "tmp"
OUTDIR = RAIZ / "output"; OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q3_base_crime.csv")

formula = "lcrmrte ~ " + " + ".join(H.RHS_POOLED)
pooled = smf.ols(formula, data=base).fit()

print(f"Pooled: N={int(pooled.nobs)}, R2={pooled.rsquared:.4f}, "
      f"b1(prbarr)={pooled.params['lprbarr']:+.4f}, b2(polpc)={pooled.params['lpolpc']:+.4f}")

# residuos + preditos para o q3_3
saida = base[["county", "year"] + H.RHS_POOLED].copy()
saida["fitted"] = pooled.fittedvalues
saida["resid"] = pooled.resid
saida["resid2"] = pooled.resid ** 2
saida.to_csv(TMPDIR / "q3_pooled_resid.csv", index=False)

ext = H.extrai(pooled)
rodape = [
    (r"Controles socioecon\^omicos", ["Sim"]),
    (r"\textit{Dummies} de regi\~ao", ["Sim"]),
    (r"Efeitos fixos de condado", [r"N\~ao"]),
    (r"Efeitos fixos de ano", [r"N\~ao"]),
    ("Erros-padrao", ["Convencional"]),
]
H.tabela_regressao(
    OUTDIR / "q3_tab_pooled.tex", [("MQO agrupado", ext)],
    [(v, H.ROT[v]) for v in H.DETERRENCIA], rodape,
    caption="MQO agrupado (\\textit{pooled}) em logaritmos",
    label="tab:q3_pooled")

# dispersao: ln(crmrte) contra ln(prbarr) e ln(polpc), com reta MQO simples
H.estilo_figuras()
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6))
fig.suptitle("Dispersão: crime e dissuasão (todas as obs., em logs)", y=0.99, fontsize=12.5)
pares = [("lprbarr", "ln(prob. de prisão)", H.COR["vermelho"]),
         ("lpolpc",  "ln(polícia per capita)", H.COR["verde"])]
for ax, (x, rot, cor) in zip(axes, pares):
    ax.scatter(base[x], base["lcrmrte"], s=10, color=cor, alpha=0.45, edgecolor="none")
    b1, b0 = np.polyfit(base[x], base["lcrmrte"], 1)
    xs = np.linspace(base[x].min(), base[x].max(), 50)
    ax.plot(xs, b0 + b1 * xs, color="0.20", lw=1.4)
    ax.set_title(f"incl. simples: {H.num(b1,2)}", fontsize=10)
    ax.set_xlabel(rot); ax.set_ylabel("ln(taxa de crime)")
fig.tight_layout(rect=(0, 0.05, 1, 0.96))
H.nota_fonte(fig)
fig.savefig(OUTDIR / "q3_fig_dispersao.pdf")
fig.savefig(OUTDIR / "q3_fig_dispersao.png", dpi=150)
plt.close(fig)

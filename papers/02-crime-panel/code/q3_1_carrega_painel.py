"""
q3_1 - carrega o painel de crime de Cornwell e Trumbull (1994) pela base
embutida wooldridge::crime4 (90 condados da Carolina do Norte, 1981-1987),
descreve o painel (N, T, balanceamento), monta a base de trabalho e gera as
estatisticas descritivas e uma figura descritiva.

Autor: Guilherme Cabral (Grupo 1)
Data: 27/06/2026
Inputs:  wooldridge::crime4 (base embutida)
Outputs: tmp/q3_base_crime.csv
         output/q3_tab_descritivas.tex
         output/q3_fig_painel_descritivo.pdf
"""
import importlib.util as _ilu
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import wooldridge as woo

_hp = Path(__file__).resolve().parent / ".q3_helpers.py"
_spec = _ilu.spec_from_file_location("q3_helpers", _hp)
H = _ilu.module_from_spec(_spec); _spec.loader.exec_module(H)

DIRETORIO_ATUAL = Path(__file__).resolve().parent
RAIZ = DIRETORIO_ATUAL.parent
TMPDIR = RAIZ / "tmp";    TMPDIR.mkdir(parents=True, exist_ok=True)
OUTDIR = RAIZ / "output"; OUTDIR.mkdir(parents=True, exist_ok=True)

# carrega a base e descreve o painel
df = woo.data("crime4")
df["ano"] = 1900 + df["year"].astype(int)

N = df["county"].nunique()
T = df["year"].nunique()
por_ano = df.groupby("year").size()
balanceado = (por_ano.nunique() == 1) and (len(df) == N * T)

print(f"Painel: N={N} condados, T={T} anos ({df['ano'].min()}-{df['ano'].max()}), "
      f"{len(df)} obs, balanceado={balanceado}")

# base de trabalho: ids + niveis + logs usados nas regressoes
niveis = [v for v, _ in H.VARS_DESCR]
logs = sorted(set(H.RHS_POOLED + H.RHS_FE + ["lcrmrte"]))
dummies_ano = [c for c in df.columns if c.startswith("d8")]
cols = ["county", "year", "ano"] + niveis + logs + dummies_ano
cols = list(dict.fromkeys([c for c in cols if c in df.columns]))
base = df[cols].copy()
base.to_csv(TMPDIR / "q3_base_crime.csv", index=False)

# tabela de descritivas (niveis)
H.tabela_descritivas(
    OUTDIR / "q3_tab_descritivas.tex", base, H.VARS_DESCR,
    caption=("Estat\\'isticas descritivas -- painel de crime (Carolina do Norte, "
             f"{df['ano'].min()}--{df['ano'].max()}; {N} condados, {len(df)} obs.)"),
    label="tab:q3_descritivas")

# figura: evolucao da taxa media de crime e distribuicao
H.estilo_figuras()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.5))
fig.suptitle("Painel de crime -- Carolina do Norte (1981--1987)", y=0.99, fontsize=12.5)

g = base.groupby("ano")["crmrte"]
m, sd = g.mean(), g.std()
ax1.plot(m.index, m.values, color=H.COR["azul"], lw=1.6, marker="o", ms=3.5)
ax1.fill_between(m.index, m - sd, m + sd, color=H.COR["azul"], alpha=0.12)
ax1.set_title("Taxa de crime média por ano ($\\pm$1 d.p.)", fontsize=10.5)
ax1.set_xlabel("Ano"); ax1.set_ylabel("Crimes por pessoa")

ax2.hist(base["crmrte"], bins=30, color=H.COR["azul"], alpha=0.8, edgecolor="white", lw=0.4)
ax2.set_title("Distribuição (todas as obs.)", fontsize=10.5)
ax2.set_xlabel("Crimes por pessoa"); ax2.set_ylabel("Frequência")

fig.tight_layout(rect=(0, 0.05, 1, 0.96))
H.nota_fonte(fig)
fig.savefig(OUTDIR / "q3_fig_painel_descritivo.pdf")
fig.savefig(OUTDIR / "q3_fig_painel_descritivo.png", dpi=150)
plt.close(fig)

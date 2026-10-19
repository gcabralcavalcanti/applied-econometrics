"""Load the Cornwell and Trumbull (1994) crime panel and describe it.

Input:   wooldridge::crime4 (90 North Carolina counties, 1981-1987, bundled with the package)
Outputs: tmp/q3_base_crime.csv              working dataset (ids, levels, logs, year dummies)
         output/q3_tab_descritivas.tex      descriptive statistics
         output/q3_fig_painel_descritivo.*  mean crime rate by year and its distribution
"""

from pathlib import Path

import matplotlib
import wooldridge as woo

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import q3_helpers as qh

ROOT = Path(__file__).resolve().parent.parent
TMPDIR = ROOT / "tmp"
OUTDIR = ROOT / "output"
TMPDIR.mkdir(parents=True, exist_ok=True)
OUTDIR.mkdir(parents=True, exist_ok=True)

df = woo.data("crime4")
df["ano"] = 1900 + df["year"].astype(int)

N = df["county"].nunique()
T = df["year"].nunique()
rows_per_year = df.groupby("year").size()
balanced = (rows_per_year.nunique() == 1) and (len(df) == N * T)

print(f"Panel: N={N} counties, T={T} years ({df['ano'].min()}-{df['ano'].max()}), {len(df)} obs, balanced={balanced}")

levels = [v for v, _ in qh.DESCRIPTIVE_VARS]
logs = sorted(set(qh.RHS_POOLED + qh.RHS_FE + ["lcrmrte"]))
year_dummies = [c for c in df.columns if c.startswith("d8")]
cols = ["county", "year", "ano"] + levels + logs + year_dummies
cols = list(dict.fromkeys([c for c in cols if c in df.columns]))
base = df[cols].copy()
base.to_csv(TMPDIR / "q3_base_crime.csv", index=False)

qh.descriptives_table(
    OUTDIR / "q3_tab_descritivas.tex",
    base,
    qh.DESCRIPTIVE_VARS,
    caption=(
        "Estat\\'isticas descritivas -- painel de crime (Carolina do Norte, "
        f"{df['ano'].min()}--{df['ano'].max()}; {N} condados, {len(df)} obs.)"
    ),
    label="tab:q3_descritivas",
)

qh.set_figure_style()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.5))
fig.suptitle("Painel de crime -- Carolina do Norte (1981--1987)", y=0.99, fontsize=12.5)

by_year = base.groupby("ano")["crmrte"]
mean, sd = by_year.mean(), by_year.std()
ax1.plot(mean.index, mean.values, color=qh.COLORS["blue"], lw=1.6, marker="o", ms=3.5)
ax1.fill_between(mean.index, mean - sd, mean + sd, color=qh.COLORS["blue"], alpha=0.12)
ax1.set_title("Taxa de crime média por ano ($\\pm$1 d.p.)", fontsize=10.5)
ax1.set_xlabel("Ano")
ax1.set_ylabel("Crimes por pessoa")

ax2.hist(base["crmrte"], bins=30, color=qh.COLORS["blue"], alpha=0.8, edgecolor="white", lw=0.4)
ax2.set_title("Distribuição (todas as obs.)", fontsize=10.5)
ax2.set_xlabel("Crimes por pessoa")
ax2.set_ylabel("Frequência")

fig.tight_layout(rect=(0, 0.05, 1, 0.96))
qh.add_source_note(fig)
fig.savefig(OUTDIR / "q3_fig_painel_descritivo.pdf")
fig.savefig(OUTDIR / "q3_fig_painel_descritivo.png", dpi=150)
plt.close(fig)

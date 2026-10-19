"""
03_analysis - persistence of performance, the cost of fees, and a Monte Carlo of selection rules.

Unit of analysis: fund-year. A fund enters year y+1's test if it was on the December-y menu (it had a retail
factsheet), so the menu is the one an investor actually saw, closed funds included.

  formation year y : excess return over the CDI, compounded over the months of y (at least 10 months)
  holding year y+1 : the same over y+1; if the fund closes mid-year the money earns the CDI for the remaining months
  cost             : expense ratio from the December-y factsheet (total expenses / net assets, last 12 months)

Returns come from quotas, which are already net of every fee charged to the fund. So in a regression of next-year
net excess return on the expense ratio, a slope of -1 means fees are a pure cost; above -1, expensive funds earn part
of their fee back before costs; below -1, they do worse even before costs.

Outputs: output/tab_persistence.tex, tab_transition.tex, tab_costs.tex, tab_montecarlo.tex, results.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "output"
OUT.mkdir(exist_ok=True)
FEE_MAX, EXPENSE_MAX, RET_MAX = 5.0, 10.0, 0.5
PAIRS = [(2021, 2022), (2022, 2023), (2023, 2024), (2024, 2025)]
CLASSES = ["Equity", "Multi-asset", "Fixed income"]
RNG = np.random.default_rng(20261019)
N_PATHS, HORIZON = 10_000, 10

# ---------------------------------------------------------------- data
menu = pd.read_csv(DATA / "menu.csv")
menu.loc[~menu["admin_fee"].between(0, FEE_MAX), "admin_fee"] = np.nan
menu.loc[~menu["expense_ratio"].between(0, EXPENSE_MAX), "expense_ratio"] = np.nan
q = pd.read_csv(DATA / "monthly_quotas.csv.gz")
q = q[q["quota"] > 0].sort_values(["fund", "month"])
q["p"] = pd.PeriodIndex(q["month"], freq="M")
gap = q.groupby("fund")["p"].diff().map(lambda d: getattr(d, "n", np.nan))
q["ret"] = np.where(gap == 1, q["quota"] / q.groupby("fund")["quota"].shift() - 1, np.nan)
q.loc[q["ret"].abs() > RET_MAX, "ret"] = np.nan
cdi = pd.read_csv(DATA / "cdi.csv").assign(cdi=lambda d: d["cdi"] / 100)
q = q.merge(cdi, on="month")
q["year"] = q["p"].dt.year
cdi_year = cdi.assign(year=pd.PeriodIndex(cdi["month"], freq="M").year).groupby("year")["cdi"].apply(
    lambda s: (1 + s).prod() - 1)


def year_returns(year: int, min_months: int) -> pd.DataFrame:
    d = q[(q["year"] == year) & q["ret"].notna()]
    g = d.groupby("fund").agg(months=("ret", "size"), gross=("ret", lambda s: (1 + s).prod()),
                              cdi_in=("cdi", lambda s: (1 + s).prod()))
    g = g[g["months"] >= min_months]
    # months without a return (fund closed or not yet open) earn the CDI
    g["total"] = g["gross"] * (1 + cdi_year[year]) / g["cdi_in"] - 1
    g["excess"] = (g["total"] - cdi_year[year]) * 100          # percentage points over the CDI
    return g[["months", "excess"]]


rows = []
for y, y1 in PAIRS:
    form = year_returns(y, 10).rename(columns={"excess": "past", "months": "past_months"})
    hold = year_returns(y1, 1).rename(columns={"excess": "next", "months": "next_months"})
    m = menu[menu["year"] == y].set_index("fund")
    d = m.join(form, how="inner").join(hold, how="left")
    d["closed"] = d["next"].isna()
    d["next"] = d["next"].fillna(0.0)    # no report in y+1 at all: treated as cash at the CDI
    d["pair"] = f"{y}-{y1}"
    size = q[(q["year"] == y) & (q["p"].dt.month == 12)].set_index("fund")["net_assets"]
    d["log_size"] = np.log(size.reindex(d.index).clip(lower=1))
    rows.append(d.reset_index())
panel = pd.concat(rows, ignore_index=True)
panel["quintile"] = panel.groupby(["pair", "asset_class"])["past"].transform(
    lambda s: pd.qcut(s.rank(method="first"), 5, labels=False) + 1)
panel["cost_tercile"] = panel.groupby(["pair", "asset_class"])["expense_ratio"].transform(
    lambda s: pd.qcut(s.rank(method="first"), 3, labels=False) + 1 if s.notna().sum() >= 3 else np.nan)
panel.to_csv(OUT / "panel_fund_year.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})


def star(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""


results = {"n_fund_years": int(len(panel)), "n_funds": int(panel["fund"].nunique()),
           "closed_share_pct": round(panel["closed"].mean() * 100, 1), "pairs": [p for p in panel["pair"].unique()]}

# ---------------------------------------------------------------- T1 persistence by quintile
# equal weight per year pair, so the quintile rows and the Q5-Q1 spread are on the same basis
t1 = panel.groupby(["asset_class", "pair", "quintile"])["next"].mean().groupby(["asset_class", "quintile"]).mean().unstack()
spread = {}
for c in CLASSES:
    s = panel[panel["asset_class"] == c].groupby(["pair", "quintile"])["next"].mean().unstack()
    diff = s[5] - s[1]
    spread[c] = (diff.mean(), diff.std(ddof=1) / np.sqrt(len(diff)), len(diff))
reg_persist = {}
for c in CLASSES:
    d = panel[panel["asset_class"] == c]
    fit = smf.ols("next ~ past + C(pair)", d).fit(cov_type="cluster", cov_kwds={"groups": d["fund"]})
    reg_persist[c] = fit
with open(OUT / "tab_persistence.tex", "w", encoding="utf-8") as f:
    f.write("\\begin{table}[htbp]\\centering\n\\caption{Next-year excess return over the CDI (p.p.) by quintile of "
            "this year's excess return (average of the four year pairs)}\n\\begin{tabular}{lccc}\n\\toprule\n& " + " & ".join(CLASSES) + " \\\\\n\\midrule\n")
    for k in range(1, 6):
        lab = {1: "Q1 (worst this year)", 5: "Q5 (best this year)"}.get(k, f"Q{k}")
        f.write(lab + "".join(f" & {t1.loc[c, k]:.2f}" for c in CLASSES) + " \\\\\n")
    f.write("\\midrule\nQ5 minus Q1" + "".join(f" & {spread[c][0]:.2f}" for c in CLASSES) + " \\\\\n")
    f.write("" + "".join(f" & ({spread[c][1]:.2f})" for c in CLASSES) + " \\\\\n")
    f.write("Slope: next on this year" + "".join(
        f" & {reg_persist[c].params['past']:.3f}{star(reg_persist[c].pvalues['past'])}" for c in CLASSES) + " \\\\\n")
    f.write("" + "".join(f" & ({reg_persist[c].bse['past']:.3f})" for c in CLASSES) + " \\\\\n")
    f.write("Fund-years" + "".join(f" & {int((panel['asset_class'] == c).sum())}" for c in CLASSES) + " \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
results["persistence"] = {c: {"q1_next": round(t1.loc[c, 1], 2), "q5_next": round(t1.loc[c, 5], 2),
                              "q5_minus_q1": round(spread[c][0], 2), "q5_minus_q1_se": round(spread[c][1], 2),
                              "slope": round(reg_persist[c].params["past"], 3),
                              "slope_p": float(f"{reg_persist[c].pvalues['past']:.3g}")} for c in CLASSES}

# ---------------------------------------------------------------- T2 transition: does the top stay on top?
alive = panel[~panel["closed"]].copy()
alive["next_quintile"] = alive.groupby(["pair", "asset_class"])["next"].transform(
    lambda s: pd.qcut(s.rank(method="first"), 5, labels=False) + 1)
with open(OUT / "tab_transition.tex", "w", encoding="utf-8") as f:
    f.write("\\begin{table}[htbp]\\centering\n\\caption{Share of funds that stay in the same quintile next year "
            "(chance = 20\\%)}\n\\begin{tabular}{lccc}\n\\toprule\n& " + " & ".join(CLASSES) + " \\\\\n\\midrule\n")
    trans = {}
    for k, lab in [(5, "Best quintile stays best (\\%)"), (1, "Worst quintile stays worst (\\%)")]:
        vals = {c: (alive[(alive["asset_class"] == c) & (alive["quintile"] == k)]["next_quintile"] == k).mean() * 100
                for c in CLASSES}
        trans[k] = vals
        f.write(lab + "".join(f" & {vals[c]:.1f}" for c in CLASSES) + " \\\\\n")
    clo = {c: panel[(panel["asset_class"] == c) & (panel["quintile"] == 1)]["closed"].mean() * 100 for c in CLASSES}
    f.write("Worst quintile closed next year (\\%)" + "".join(f" & {clo[c]:.1f}" for c in CLASSES) + " \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
results["transition"] = {c: {"best_stays_best_pct": round(trans[5][c], 1), "worst_stays_worst_pct": round(trans[1][c], 1),
                             "worst_closed_pct": round(clo[c], 1)} for c in CLASSES}

# ---------------------------------------------------------------- T3 costs
cost = panel.dropna(subset=["expense_ratio"])
fits = {}
for c in CLASSES:
    d = cost[cost["asset_class"] == c]
    fits[c] = smf.ols("next ~ expense_ratio + past + log_size + perf_fee + C(pair)", d.dropna(subset=["log_size"])).fit(
        cov_type="cluster", cov_kwds={"groups": d.dropna(subset=["log_size"])["fund"]})
terc = cost.groupby(["asset_class", "cost_tercile"])["next"].mean().unstack()
med_cost = cost.groupby(["asset_class", "cost_tercile"])["expense_ratio"].median().unstack()
with open(OUT / "tab_costs.tex", "w", encoding="utf-8") as f:
    f.write("\\begin{table}[htbp]\\centering\n\\caption{Fees and next-year net excess return over the CDI (p.p.)}\n"
            "\\begin{tabular}{lccc}\n\\toprule\n& " + " & ".join(CLASSES) + " \\\\\n\\midrule\n")
    f.write("Expense ratio (slope)" + "".join(
        f" & {fits[c].params['expense_ratio']:.3f}{star(fits[c].pvalues['expense_ratio'])}" for c in CLASSES) + " \\\\\n")
    f.write("" + "".join(f" & ({fits[c].bse['expense_ratio']:.3f})" for c in CLASSES) + " \\\\\n")
    f.write("Performance fee (dummy)" + "".join(
        f" & {fits[c].params['perf_fee[T.True]']:.3f}{star(fits[c].pvalues['perf_fee[T.True]'])}" for c in CLASSES) + " \\\\\n")
    f.write("" + "".join(f" & ({fits[c].bse['perf_fee[T.True]']:.3f})" for c in CLASSES) + " \\\\\n")
    f.write("Observations" + "".join(f" & {int(fits[c].nobs)}" for c in CLASSES) + " \\\\\n")
    f.write("$R^2$" + "".join(f" & {fits[c].rsquared:.3f}" for c in CLASSES) + " \\\\\n\\midrule\n")
    for k, lab in [(1, "Cheapest third"), (2, "Middle third"), (3, "Most expensive third")]:
        f.write(f"{lab}: next-year excess" + "".join(f" & {terc.loc[c, k]:.2f}" for c in CLASSES) + " \\\\\n")
        f.write(f"{lab}: median expense ratio" + "".join(f" & {med_cost.loc[c, k]:.2f}" for c in CLASSES) + " \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
results["costs"] = {c: {"slope": round(fits[c].params["expense_ratio"], 3),
                        "slope_se": round(fits[c].bse["expense_ratio"], 3),
                        "slope_p": float(f"{fits[c].pvalues['expense_ratio']:.3g}"),
                        "cheap_third_next": round(terc.loc[c, 1], 2), "expensive_third_next": round(terc.loc[c, 3], 2),
                        "cheap_third_median_cost": round(med_cost.loc[c, 1], 2),
                        "expensive_third_median_cost": round(med_cost.loc[c, 3], 2)} for c in CLASSES}

# ---------------------------------------------------------------- T4 Monte Carlo of selection rules
# Each simulated year draws one of the observed year pairs, then one fund chosen by the rule from that year's menu,
# and applies its realised next-year net excess return. Wealth is measured relative to staying in the CDI.
RULES = {"Random fund": lambda d: d,
         "Cheapest third": lambda d: d[d["cost_tercile"] == 1],
         "Last year's best quintile": lambda d: d[d["quintile"] == 5],
         "Cheapest third, not in worst quintile": lambda d: d[(d["cost_tercile"] == 1) & (d["quintile"] > 1)]}
mc = {}
for c in CLASSES:
    by_pair = {p: g for p, g in cost[cost["asset_class"] == c].groupby("pair")}
    pairs = list(by_pair)
    for name, rule in RULES.items():
        pools = {p: rule(by_pair[p])["next"].to_numpy() / 100 for p in pairs}
        draws = np.ones(N_PATHS)
        for _ in range(HORIZON):
            pick = RNG.integers(len(pairs), size=N_PATHS)
            ex = np.array([RNG.choice(pools[pairs[i]]) for i in pick])
            draws *= 1 + ex / (1 + cdi_year.loc[2022:2025].mean())   # excess -> relative growth vs the CDI
        mc[(c, name)] = draws
with open(OUT / "tab_montecarlo.tex", "w", encoding="utf-8") as f:
    f.write("\\begin{table}[htbp]\\centering\n\\caption{Monte Carlo over 10 years: wealth relative to staying in the "
            f"CDI (1.00 = same as the CDI), {N_PATHS} paths}}\n\\begin{{tabular}}{{lcccc}}\n\\toprule\n"
            "Class: rule & Median & P5 & P95 & Beats CDI (\\%) \\\\\n\\midrule\n")
    for c in CLASSES:
        for name in RULES:
            w = mc[(c, name)]
            f.write(f"{c}: {name} & {np.median(w):.2f} & {np.percentile(w, 5):.2f} & {np.percentile(w, 95):.2f} & "
                    f"{(w > 1).mean() * 100:.0f} \\\\\n")
        f.write("\\midrule\n" if c != CLASSES[-1] else "")
    f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
results["montecarlo"] = {c: {name: {"median": round(float(np.median(mc[(c, name)])), 2),
                                    "p5": round(float(np.percentile(mc[(c, name)], 5)), 2),
                                    "p95": round(float(np.percentile(mc[(c, name)], 95)), 2),
                                    "beats_cdi_pct": round(float((mc[(c, name)] > 1).mean() * 100), 0)}
                             for name in RULES} for c in CLASSES}
(OUT / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
print(json.dumps(results, indent=1))


# ---------------------------------------------------------------- figures
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

COLORS = {"Equity": "#2a78d6", "Multi-asset": "#eb6834", "Fixed income": "#1baf7a"}
INK, MUTED = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.hashsalt": "aecon", "pdf.fonttype": 42})

fig, ax = plt.subplots(figsize=(6.4, 3.4))
width = 0.26
for i, c in enumerate(CLASSES):
    vals = [terc.loc[c, k] for k in (1, 2, 3)]
    xs = np.arange(3) + (i - 1) * (width + 0.02)
    ax.bar(xs, vals, width, color=COLORS[c], label=c)
    ax.text(xs[2], vals[2] + 0.12, f"{vals[2]:.1f}", ha="center", va="bottom", fontsize=8, color="white")
ax.axhline(0, color=MUTED, lw=0.8)
ax.set_xticks(range(3), ["Cheapest third", "Middle third", "Most expensive third"])
ax.set_ylabel("Next-year excess over CDI (p.p.)")
ax.set_title("The most expensive third lost the most to the CDI", loc="left", fontsize=10, color=INK)
ax.legend(frameon=False, ncol=3, loc="lower left", fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "fig_costs.png", dpi=160, metadata={"Software": None})
plt.close(fig)

fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.9), sharey=True)
names = list(RULES)
for ax, c in zip(axes, CLASSES):
    for j, name in enumerate(names):
        w = mc[(c, name)]
        lo, med, hi = np.percentile(w, 5), np.median(w), np.percentile(w, 95)
        ax.plot([lo, hi], [j, j], color=COLORS[c], lw=2, solid_capstyle="round")
        ax.plot(med, j, "o", ms=6, color=COLORS[c], mec="white", mew=1.2)
        ax.text(med, j - 0.18, f"{med:.2f}", ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.axvline(1, color=MUTED, lw=0.8, ls="--")
    ax.set_title(c, fontsize=9, color=INK, loc="left")
axes[0].set_yticks(range(len(names)), names, fontsize=8)
axes[0].set_ylim(len(names) - 0.5, -0.8)
fig.supxlabel("Wealth after 10 years relative to the CDI", fontsize=9, color=INK)
fig.suptitle("Monte Carlo: median (dot) and 5th-95th percentile (line); 1.00 = same as the CDI",
             x=0.01, ha="left", fontsize=9, color=INK)
fig.tight_layout()
fig.savefig(OUT / "fig_montecarlo.png", dpi=160, metadata={"Software": None})
plt.close(fig)

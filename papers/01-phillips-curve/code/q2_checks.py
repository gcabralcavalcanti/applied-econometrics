"""Data checks on the raw BCB series and on the monthly base, run before any regression.

What could go wrong silently, and the check that catches it:
 - a month missing from one series (the join would drop it)  -> month continuity
 - IPCA downloaded as 12-month instead of monthly %          -> unit check on the median
 - Focus expectation not aligned to t+1                       -> coverage of t+1 readings
 - Focus and IPCA in different units                          -> mean gap between them
 - breaks (COVID, 2015-16)                                    -> large-jump warning

Inputs:  tmp/q2_ipca.csv, tmp/q2_desemprego.csv, tmp/q2_focus_mensal.csv, tmp/q2_base_phillips.csv
Outputs: output/data_checks.json
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent.parent))
from applied_econometrics.checks import WARN, Report

TMP_DIR = ROOT / "tmp"
ipca = pd.read_csv(TMP_DIR / "q2_ipca.csv", parse_dates=["Date"])
unemployment = pd.read_csv(TMP_DIR / "q2_desemprego.csv", parse_dates=["Date"])
focus = pd.read_csv(TMP_DIR / "q2_focus_mensal.csv")
df = pd.read_csv(TMP_DIR / "q2_base_phillips.csv", parse_dates=["data"])

r = Report(
    "01-phillips-curve",
    [TMP_DIR / f for f in ("q2_ipca.csv", "q2_desemprego.csv", "q2_focus_mensal.csv", "q2_base_phillips.csv")],
)

# raw series
r.no_missing(ipca, ["ipca"], "missing values: IPCA (SGS 433)")
r.monthly_continuity(ipca["Date"], "IPCA")
r.in_range(ipca["ipca"], -1.5, 3.5, "IPCA monthly change", "% per month")
r.add(
    "unit: IPCA is the monthly rate, not 12-month",
    ipca["ipca"].median() < 1.5,
    f"median {ipca['ipca'].median():.2f}% (a 12-month series would sit near 4-6%)",
    ipca["ipca"].median(),
)
r.no_missing(unemployment, ["desemprego"], "missing values: unemployment (SGS 24369)")
r.monthly_continuity(unemployment["Date"], "unemployment")
r.in_range(unemployment["desemprego"], 3, 20, "unemployment rate", "%")

parsed = pd.to_datetime(focus["DataReferencia"], format="%m/%Y", errors="coerce")
r.add(
    "Focus reference month parses as MM/YYYY",
    parsed.notna().all(),
    f"{int(parsed.isna().sum())} unparseable of {len(focus)}",
    int(parsed.isna().sum()),
)
r.in_range(focus["Mediana"], -1.5, 3.5, "Focus median expectation", "% per month")

# timing: every month in the window needs a reading made in t for t+1
fm = focus.assign(t=pd.to_datetime(focus["Data"]).dt.to_period("M"), ref=parsed.dt.to_period("M"))
has_next = set(fm.loc[fm["ref"] == fm["t"] + 1, "t"])
window = pd.period_range(df["data"].min(), df["data"].max(), freq="M")
missing_t1 = [str(m) for m in window if m not in has_next]
r.add(
    "timing: a t+1 Focus reading exists for every month t",
    not missing_t1,
    "all months covered" if not missing_t1 else f"missing: {missing_t1[:10]}",
    len(missing_t1),
)

# the base used by the regressions
r.no_missing(df, ["ipca", "desemprego", "exp_ipca_prox"], "missing values: regression base")
r.no_duplicates(df, ["data"])
r.monthly_continuity(df["data"], "regression base")
starts = [ipca["Date"].min(), unemployment["Date"].min()]
r.add(
    "window starts where the shortest series starts (PNAD Continua)",
    df["data"].min() >= max(starts),
    f"base starts {df['data'].min().date()}",
    str(df["data"].min().date()),
)
gap = (df["exp_ipca_prox"] - df["ipca"]).abs().mean()
r.add(
    "unit: expectation and realised IPCA on the same scale",
    gap < 1.0,
    f"mean absolute gap {gap:.2f} p.p. per month",
    gap,
)
r.jumps(df["ipca"], df["data"], "IPCA")
r.jumps(df["desemprego"], df["data"], "unemployment")
covid = df[(df["data"] >= "2020-03-01") & (df["data"] <= "2021-06-01")]
r.add(
    "break window present: COVID (2020-03 to 2021-06)",
    covid.empty,
    f"{len(covid)} months inside the window; q2_7 re-estimates without them",
    len(covid),
    WARN,
)

r.finish(ROOT / "output" / "data_checks.json")

"""
02_checks - automatic checks on the fund menu, the month-end quotas and the CDI, before any model runs.
Writes output/data_checks.json.

What could silently go wrong here, and the check that catches it:
 - fees typed in the wrong unit (bps or R$ in a % field)      -> range checks; out-of-range values become missing
 - negative or absurd expense ratios                           -> same
 - the CVM 175 transition shrinking the factsheet file         -> menu size by year
 - quota jumps from splits or typos (a 300% month)             -> extreme-return check; those months are dropped
 - CDI in the wrong unit or with a gap                         -> continuity and range
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent.parent))
from aecon.checks import Report, WARN  # noqa: E402

DATA = ROOT / "data"
FEE_MAX, EXPENSE_MAX, RET_MAX = 5.0, 10.0, 0.5

menu = pd.read_csv(DATA / "menu.csv")
q = pd.read_csv(DATA / "monthly_quotas.csv.gz")
cdi = pd.read_csv(DATA / "cdi.csv")
r = Report("04-fund-selection", [DATA / "menu.csv", DATA / "monthly_quotas.csv.gz", DATA / "cdi.csv"])

# menu
r.no_duplicates(menu, ["year", "fund"])
sizes = menu.groupby("year").size()
r.add("menu size stable across years", sizes.min() > 0.5 * sizes.max(),
      "funds with a December factsheet: " + ", ".join(f"{y}: {n}" for y, n in sizes.items())
      + ". After CVM Resolution 175 (2024) far fewer factsheets reach the open-data file", sizes.to_dict(), WARN)
bad_fee = ((menu["admin_fee"] < 0) | (menu["admin_fee"] > FEE_MAX)).sum()
r.add(f"admin fee within 0-{FEE_MAX}% a year", bad_fee == 0,
      f"{bad_fee} of {menu['admin_fee'].notna().sum()} values outside (max {menu['admin_fee'].max():,.0f}); "
      "set to missing", int(bad_fee), WARN)
bad_exp = ((menu["expense_ratio"] < 0) | (menu["expense_ratio"] > EXPENSE_MAX)).sum()
r.add(f"expense ratio within 0-{EXPENSE_MAX}% of net assets", bad_exp == 0,
      f"{bad_exp} of {menu['expense_ratio'].notna().sum()} values outside (min {menu['expense_ratio'].min():.2f}, "
      f"max {menu['expense_ratio'].max():,.0f}); set to missing", int(bad_exp), WARN)
r.add("every menu fund has an asset class", menu["asset_class"].notna().all(), "Equity, Multi-asset, Fixed income",
      menu["asset_class"].value_counts().to_dict())

# quotas
r.no_duplicates(q, ["fund", "month"])
nonpos = int((q["quota"] <= 0).sum())
r.add("quotas are positive", nonpos == 0, f"{nonpos} of {len(q):,} fund-months with quota <= 0 (funds being wound "
      "up); dropped", nonpos, WARN)
months = pd.period_range(q["month"].min(), q["month"].max(), freq="M")
r.add("every month 2021-01 to 2026-09 has quotas", len(months) == q["month"].nunique() == 69,
      f"{q['month'].nunique()} months", q["month"].nunique())
found = menu["fund"].isin(q["fund"]).mean()
r.add("menu funds found in the daily reports", found > 0.9, f"{found:.1%} of fund-years", found, WARN)
q = q.sort_values(["fund", "month"])
q["p"] = pd.PeriodIndex(q["month"], freq="M")
consecutive = q.groupby("fund")["p"].diff().map(lambda d: getattr(d, "n", np.nan)) == 1
ret = (q["quota"] / q.groupby("fund")["quota"].shift() - 1)[consecutive]
extreme = int((ret.abs() > RET_MAX).sum())
r.add(f"no month-end return beyond ±{RET_MAX:.0%}", extreme == 0,
      f"{extreme} of {len(ret):,} fund-months (quota splits or typos); dropped from the returns", extreme, WARN)

# CDI
r.monthly_continuity(pd.to_datetime(cdi["month"]), "CDI")
r.in_range(cdi["cdi"], 0.1, 1.5, "CDI", "% per month")

r.finish(ROOT / "output" / "data_checks.json")

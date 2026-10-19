"""
q3_checks - automatic checks on the crime panel, run after q3_1 builds the base and before
any regression. Writes output/data_checks.json.

What could silently go wrong here, and the check that catches it:
 - an unbalanced panel (fixed effects and clustering assume 90 x 7)  -> balance check
 - log variables that do not match their levels                       -> log consistency
 - "probabilities" above 1 (a known quirk of this dataset)            -> range warning
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ.parent.parent))
from aecon.checks import Report, WARN  # noqa: E402

base = pd.read_csv(RAIZ / "tmp" / "q3_base_crime.csv")
r = Report("02-crime-panel", [RAIZ / "tmp" / "q3_base_crime.csv"])

N, T = base["county"].nunique(), base["year"].nunique()
r.add("balanced panel: 90 counties x 7 years", (N, T, len(base)) == (90, 7, 630),
      f"N={N}, T={T}, rows={len(base)}", {"N": N, "T": T, "rows": len(base)})
r.no_duplicates(base, ["county", "year"])
used = ["lcrmrte", "lprbarr", "lprbconv", "lprbpris", "lavgsen", "lpolpc"]
r.no_missing(base, used, "missing values: regression variables")
for lv, lvl in [("lcrmrte", "crmrte"), ("lprbarr", "prbarr"), ("lpolpc", "polpc"), ("lavgsen", "avgsen")]:
    err = float((base[lv] - np.log(base[lvl])).abs().max())
    r.add(f"log consistency: {lv} = log({lvl})", err < 1e-4, f"max abs difference {err:.2e}", err)
r.in_range(base["crmrte"], 0, 1, "crime rate", "crimes per person")
r.in_range(base["polpc"], 0, 0.05, "police per capita", "officers per person")
# arrests/offences and convictions/arrests are ratios of counts, not true probabilities
r.in_range(base["prbarr"], 0, 1, "P(arrest) = arrests / offences", "", WARN)
r.in_range(base["prbconv"], 0, 1, "P(conviction) = convictions / arrests", "", WARN)
r.in_range(base["year"], 81, 87, "year", "(1981-1987)")

r.finish(RAIZ / "output" / "data_checks.json")

"""Two-way fixed effects (county + year), compared with county effects only.

Year effects absorb statewide shocks that hit every county in the same year.

Input:  tmp/q3_base_crime.csv
Output: output/q3_tab_duas_vias.tex
"""

from pathlib import Path

import pandas as pd
import q3_helpers as qh
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parent.parent
TMPDIR = ROOT / "tmp"
OUTDIR = ROOT / "output"
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q3_base_crime.csv")
panel = base.set_index(["county", "year"])

rhs = " + ".join(qh.RHS_FE)
fe = PanelOLS.from_formula("lcrmrte ~ 1 + " + rhs + " + EntityEffects", data=panel).fit()
fe2 = PanelOLS.from_formula("lcrmrte ~ 1 + " + rhs + " + EntityEffects + TimeEffects", data=panel).fit()

print(f"b1(prbarr): FE={fe.params['lprbarr']:+.4f} -> two-way={fe2.params['lprbarr']:+.4f}")
print(f"b2(polpc):  FE={fe.params['lpolpc']:+.4f} -> two-way={fe2.params['lpolpc']:+.4f}")

footer = [
    (r"Efeitos fixos de condado", ["Sim", "Sim"]),
    (r"Efeitos fixos de ano", [r"N\~ao", "Sim"]),
    ("Erros-padrao", ["Convencional", "Convencional"]),
]
qh.regression_table(
    OUTDIR / "q3_tab_duas_vias.tex",
    [("EF condado", qh.extract(fe)), ("EF duas vias", qh.extract(fe2))],
    [(v, qh.LABELS[v]) for v in qh.DETERRENCE],
    footer,
    caption="Efeitos fixos de condado vs.\\ painel de duas vias (condado $+$ ano)",
    label="tab:q3_duas_vias",
    note=(
        "Erros-padrao entre parenteses. *** p$<$0,01; ** p$<$0,05; * p$<$0,10. "
        "Dep.: ln(taxa de crime). $R^2$ \\textit{within}. Os efeitos fixos de ano "
        "captam choques macro comuns a todos os condados em cada ano."
    ),
)

"""County fixed effects (within) with PanelOLS, compared with pooled OLS.

Input:  tmp/q3_base_crime.csv
Output: output/q3_tab_fe_condado.tex
"""

from pathlib import Path

import pandas as pd
import q3_helpers as qh
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parent.parent
TMPDIR = ROOT / "tmp"
OUTDIR = ROOT / "output"
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q3_base_crime.csv")
panel = base.set_index(["county", "year"])

pooled = smf.ols("lcrmrte ~ " + " + ".join(qh.RHS_POOLED), data=base).fit()
fe = PanelOLS.from_formula("lcrmrte ~ 1 + " + " + ".join(qh.RHS_FE) + " + EntityEffects", data=panel).fit()

print(f"b1(prbarr): pooled={pooled.params['lprbarr']:+.4f} -> FE={fe.params['lprbarr']:+.4f}")
print(f"b2(polpc):  pooled={pooled.params['lpolpc']:+.4f} -> FE={fe.params['lpolpc']:+.4f}")

footer = [
    (r"Controles socioecon\^omicos", ["Sim", "Absorvidos"]),
    (r"Efeitos fixos de condado", [r"N\~ao", "Sim"]),
    (r"Efeitos fixos de ano", [r"N\~ao", r"N\~ao"]),
    ("Erros-padrao", ["Convencional", "Convencional"]),
]
qh.regression_table(
    OUTDIR / "q3_tab_fe_condado.tex",
    [("MQO agrupado", qh.extract(pooled)), ("EF de condado", qh.extract(fe))],
    [(v, qh.LABELS[v]) for v in qh.DETERRENCE],
    footer,
    caption="MQO agrupado vs.\\ efeitos fixos de condado (\\textit{within})",
    label="tab:q3_fe_condado",
    note=(
        "Erros-padrao entre parenteses. *** p$<$0,01; ** p$<$0,05; * p$<$0,10. "
        "Dep.: ln(taxa de crime). $R^2$ do EF e \\textit{within}. Controles invariantes "
        "no tempo (regiao, densidade, demografia) sao absorvidos pelos efeitos fixos."
    ),
)

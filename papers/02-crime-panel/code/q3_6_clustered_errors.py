"""Two-way fixed effects with standard errors clustered by county, compared with conventional ones.

Clustering allows the errors of the same county to be correlated across years.

Input:  tmp/q3_base_crime.csv
Output: output/q3_tab_cluster.tex
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
formula = "lcrmrte ~ 1 + " + " + ".join(qh.RHS_FE) + " + EntityEffects + TimeEffects"

conventional = PanelOLS.from_formula(formula, data=panel).fit()
clustered = PanelOLS.from_formula(formula, data=panel).fit(cov_type="clustered", cluster_entity=True)

for v in ["lprbarr", "lpolpc"]:
    print(f"{v}: conventional SE={conventional.std_errors[v]:.4f} -> clustered={clustered.std_errors[v]:.4f}")

footer = [
    (r"Efeitos fixos de condado", ["Sim", "Sim"]),
    (r"Efeitos fixos de ano", ["Sim", "Sim"]),
    ("Erros-padrao", ["Convencional", "Cluster (condado)"]),
]
qh.regression_table(
    OUTDIR / "q3_tab_cluster.tex",
    [("Convencional", qh.extract(conventional)), ("Cluster", qh.extract(clustered))],
    [(v, qh.LABELS[v]) for v in qh.DETERRENCE],
    footer,
    caption="Painel de duas vias: erros convencionais vs.\\ clusterizados por condado",
    label="tab:q3_cluster",
    note=(
        "Coeficientes identicos (mesma estimacao); muda so o erro-padrao. *** p$<$0,01; "
        "** p$<$0,05; * p$<$0,10. Dep.: ln(taxa de crime). O cluster por condado admite "
        "correlacao serial arbitraria dentro de cada condado."
    ),
)

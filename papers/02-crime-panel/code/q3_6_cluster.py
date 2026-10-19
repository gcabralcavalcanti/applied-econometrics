"""
q3_6 - reestima o painel de duas vias com erros-padrao clusterizados por condado
e compara com os convencionais. O cluster corrige a correlacao serial dos erros
dentro de cada condado ao longo dos anos.

Autor: Guilherme Cabral (Grupo 1)
Data: 27/06/2026
Inputs:  tmp/q3_base_crime.csv
Outputs: output/q3_tab_cluster.tex
"""
import importlib.util as _ilu
from pathlib import Path
import pandas as pd
from linearmodels.panel import PanelOLS

_hp = Path(__file__).resolve().parent / ".q3_helpers.py"
_spec = _ilu.spec_from_file_location("q3_helpers", _hp)
H = _ilu.module_from_spec(_spec); _spec.loader.exec_module(H)

RAIZ = Path(__file__).resolve().parent.parent
TMPDIR = RAIZ / "tmp"; OUTDIR = RAIZ / "output"; OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q3_base_crime.csv")
painel = base.set_index(["county", "year"])
f = "lcrmrte ~ 1 + " + " + ".join(H.RHS_FE) + " + EntityEffects + TimeEffects"

conv = PanelOLS.from_formula(f, data=painel).fit()
clu = PanelOLS.from_formula(f, data=painel).fit(cov_type="clustered", cluster_entity=True)

for v in ["lprbarr", "lpolpc"]:
    print(f"{v}: SE convencional={conv.std_errors[v]:.4f} -> cluster={clu.std_errors[v]:.4f}")

rodape = [
    (r"Efeitos fixos de condado", ["Sim", "Sim"]),
    (r"Efeitos fixos de ano", ["Sim", "Sim"]),
    ("Erros-padrao", ["Convencional", "Cluster (condado)"]),
]
H.tabela_regressao(
    OUTDIR / "q3_tab_cluster.tex",
    [("Convencional", H.extrai(conv)), ("Cluster", H.extrai(clu))],
    [(v, H.ROT[v]) for v in H.DETERRENCIA], rodape,
    caption="Painel de duas vias: erros convencionais vs.\\ clusterizados por condado",
    label="tab:q3_cluster",
    nota=("Coeficientes identicos (mesma estimacao); muda so o erro-padrao. *** p$<$0,01; "
          "** p$<$0,05; * p$<$0,10. Dep.: ln(taxa de crime). O cluster por condado admite "
          "correlacao serial arbitraria dentro de cada condado."))

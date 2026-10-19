"""
q3_4 - estima o modelo de efeitos fixos de condado (within) com
linearmodels.PanelOLS e compara a elasticidade-dissuasao (b1 ln(prbarr),
b2 ln(polpc)) com a do MQO agrupado.

Autor: Guilherme Cabral (Grupo 1)
Data: 27/06/2026
Inputs:  tmp/q3_base_crime.csv
Outputs: output/q3_tab_fe_condado.tex
"""
import importlib.util as _ilu
from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS

_hp = Path(__file__).resolve().parent / ".q3_helpers.py"
_spec = _ilu.spec_from_file_location("q3_helpers", _hp)
H = _ilu.module_from_spec(_spec); _spec.loader.exec_module(H)

RAIZ = Path(__file__).resolve().parent.parent
TMPDIR = RAIZ / "tmp"; OUTDIR = RAIZ / "output"; OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q3_base_crime.csv")
painel = base.set_index(["county", "year"])

pooled = smf.ols("lcrmrte ~ " + " + ".join(H.RHS_POOLED), data=base).fit()
fe = PanelOLS.from_formula("lcrmrte ~ 1 + " + " + ".join(H.RHS_FE) + " + EntityEffects",
                           data=painel).fit()

print(f"b1(prbarr): pooled={pooled.params['lprbarr']:+.4f} -> FE={fe.params['lprbarr']:+.4f}")
print(f"b2(polpc):  pooled={pooled.params['lpolpc']:+.4f} -> FE={fe.params['lpolpc']:+.4f}")

rodape = [
    (r"Controles socioecon\^omicos", ["Sim", "Absorvidos"]),
    (r"Efeitos fixos de condado", [r"N\~ao", "Sim"]),
    (r"Efeitos fixos de ano", [r"N\~ao", r"N\~ao"]),
    ("Erros-padrao", ["Convencional", "Convencional"]),
]
H.tabela_regressao(
    OUTDIR / "q3_tab_fe_condado.tex",
    [("MQO agrupado", H.extrai(pooled)), ("EF de condado", H.extrai(fe))],
    [(v, H.ROT[v]) for v in H.DETERRENCIA], rodape,
    caption="MQO agrupado vs.\\ efeitos fixos de condado (\\textit{within})",
    label="tab:q3_fe_condado",
    nota=("Erros-padrao entre parenteses. *** p$<$0,01; ** p$<$0,05; * p$<$0,10. "
          "Dep.: ln(taxa de crime). $R^2$ do EF e \\textit{within}. Controles invariantes "
          "no tempo (regiao, densidade, demografia) sao absorvidos pelos efeitos fixos."))

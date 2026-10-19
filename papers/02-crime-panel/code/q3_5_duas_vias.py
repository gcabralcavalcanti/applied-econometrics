"""
q3_5 - acrescenta efeitos fixos de ano ao modelo de efeitos fixos de condado
(painel de duas vias), para captar choques nacionais comuns a todos os condados
em cada ano, e compara com o modelo so de condado.

Autor: Guilherme Cabral (Grupo 1)
Data: 27/06/2026
Inputs:  tmp/q3_base_crime.csv
Outputs: output/q3_tab_duas_vias.tex
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

rhs = " + ".join(H.RHS_FE)
fe = PanelOLS.from_formula("lcrmrte ~ 1 + " + rhs + " + EntityEffects", data=painel).fit()
fe2 = PanelOLS.from_formula("lcrmrte ~ 1 + " + rhs + " + EntityEffects + TimeEffects",
                            data=painel).fit()

print(f"b1(prbarr): FE={fe.params['lprbarr']:+.4f} -> 2vias={fe2.params['lprbarr']:+.4f}")
print(f"b2(polpc):  FE={fe.params['lpolpc']:+.4f} -> 2vias={fe2.params['lpolpc']:+.4f}")

rodape = [
    (r"Efeitos fixos de condado", ["Sim", "Sim"]),
    (r"Efeitos fixos de ano", [r"N\~ao", "Sim"]),
    ("Erros-padrao", ["Convencional", "Convencional"]),
]
H.tabela_regressao(
    OUTDIR / "q3_tab_duas_vias.tex",
    [("EF condado", H.extrai(fe)), ("EF duas vias", H.extrai(fe2))],
    [(v, H.ROT[v]) for v in H.DETERRENCIA], rodape,
    caption="Efeitos fixos de condado vs.\\ painel de duas vias (condado $+$ ano)",
    label="tab:q3_duas_vias",
    nota=("Erros-padrao entre parenteses. *** p$<$0,01; ** p$<$0,05; * p$<$0,10. "
          "Dep.: ln(taxa de crime). $R^2$ \\textit{within}. Os efeitos fixos de ano "
          "captam choques macro comuns a todos os condados em cada ano."))

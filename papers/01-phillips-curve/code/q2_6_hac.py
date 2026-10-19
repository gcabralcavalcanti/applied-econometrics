"""
q2_6 - item 6: erros-padrao HAC (Newey-West). O q2_4 mostrou que os residuos
ainda tem autocorrelacao (e talvez heterocedasticidade), entao os erros-padrao
de MQO ficam inconsistentes. Aqui reestimo a dinamica com a matriz HAC de
Newey-West e comparo, lado a lado, a significancia dos parametros sob MQO usual
vs. HAC.

Autor: Guilherme Cabral (Grupo 1)
Data: 17/06/2026
Inputs:  tmp/q2_base_phillips.csv   (do q2_2)
Outputs: output/q2_tab_hac_comparacao.tex
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from stargazer.stargazer import Stargazer

# caminhos (raiz pelo proprio arquivo)
DIRETORIO_ATUAL = Path(__file__).resolve().parent
RAIZ = DIRETORIO_ATUAL.parent
TMPDIR = RAIZ / "tmp"                        # base intermediaria (entrada)
OUTDIR = RAIZ / "output"                     # saidas finais (tabelas/figuras)
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")
base = base.assign(ipca_lag1=base["ipca"].shift(1))
amostra = base.dropna()

FORMULA = "ipca ~ desemprego + ipca_lag1 + exp_ipca_prox"

# bandwidth do HAC pela regra automatica L = floor(4*(n/100)^(2/9)),
# o "plug-in" classico de Newey-West citado em Greene. Para n=169 da L=4.
n = int(amostra.shape[0])
L = int(np.floor(4 * (n / 100) ** (2 / 9)))

mqo = smf.ols(FORMULA, data=amostra).fit()
hac = smf.ols(FORMULA, data=amostra).fit(cov_type="HAC", cov_kwds={"maxlags": L})

# tabela: mesmos coeficientes, erros-padrao MQO vs. HAC
# (o stargazer le erros-padrao e p-valores de cada modelo ajustado, entao o
#  segundo ja entra com os numeros do HAC)
sg = Stargazer([mqo, hac])
sg.dependent_variable_name("IPCA mensal")
sg.title("Modelo dinâmico: erros-padrão MQO usual vs.\\ HAC (Newey--West)")
sg.custom_columns(["MQO usual", f"MQO + HAC ($L={L}$)"], [1, 1])
sg.rename_covariates({
    "desemprego": "Desemprego $u_t$",
    "ipca_lag1": r"Inflação defasada $\pi_{t-1}$",
    "exp_ipca_prox": r"Expectativa $E_t[\pi_{t+1}]$",
})
sg.covariate_order(["desemprego", "ipca_lag1", "exp_ipca_prox", "Intercept"])
sg.show_f_statistic = False     # o F do HAC nao e diretamente comparavel ao do MQO
(OUTDIR / "q2_tab_hac_comparacao.tex").write_text(sg.render_latex(), encoding="utf-8")

# numeros-chave pra interpretacao (item 6)
print("=== Erros HAC (Newey-West) no modelo dinamico ===")
print(f"  Amostra: n={n}   defasagens HAC: L = floor(4*(n/100)^(2/9)) = {L}")
print(f"  {'variavel':16s} {'coef':>9s} {'se_MQO':>9s} {'se_HAC':>9s} {'p_MQO':>8s} {'p_HAC':>8s}")
for k in ["desemprego", "ipca_lag1", "exp_ipca_prox"]:
    print(f"  {k:16s} {mqo.params[k]:9.4f} {mqo.bse[k]:9.4f} {hac.bse[k]:9.4f} "
          f"{mqo.pvalues[k]:8.4f} {hac.pvalues[k]:8.4f}")
print("\n  Leitura: os coeficientes nao mudam (HAC so corrige os erros-padrao).")
print("  A inercia e a expectativa seguem fortemente significativas; o desemprego")
print("  segue nao-significativo. O HAC altera as magnitudes dos erros (sobe o da")
print("  expectativa, desce o da inercia), mas nao inverte nenhuma conclusao.")
# robustez do HAC a escolha de L: a conclusao nao pode depender de L
print("\n  Robustez a defasagem do HAC (L):")
print(f"    {'L':>3s}  {'p(u)':>7s}  {'p(pi_lag)':>11s}  {'p(E[pi])':>11s}")
for Lr in (4, 8, 12):
    h = smf.ols(FORMULA, data=amostra).fit(cov_type="HAC", cov_kwds={"maxlags": Lr})
    print(f"    {Lr:>3d}  {h.pvalues['desemprego']:>7.3f}  "
          f"{h.pvalues['ipca_lag1']:>11.2e}  {h.pvalues['exp_ipca_prox']:>11.2e}")
print("    -> inercia e expectativa significantes, desemprego nao-signif., para todo L.")
print("\nArquivo salvo em output/: q2_tab_hac_comparacao.tex")

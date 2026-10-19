"""
q2_7 - checagens de robustez da dinamica (reforco, alem dos itens obrigatorios).
Reestimo a Phillips dinamica sob 3 perturbacoes pra ver se a leitura central
(inercia e expectativa mandam; desemprego mudo) se mantem:
 (a) + dummies sazonais mensais -> ve se a autocorrelacao que sobrou no q2_5 era
     so sazonalidade do IPCA;
 (b) sem o periodo da COVID (2020-03 a 2021-06) -> ve se os outliers da pandemia
     estao puxando o resultado;
 (c) + tendencia linear -> proxy grosseira pra uma NAIRU caindo (uso o nivel do
     desemprego, nao o hiato u - u*).

Autor: Guilherme Cabral (Grupo 1)
Data: 17/06/2026
Inputs:  tmp/q2_base_phillips.csv   (do q2_2)
Outputs: output/q2_tab_robustez.tex
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
from stargazer.stargazer import Stargazer

# caminhos (raiz pelo proprio arquivo)
DIRETORIO_ATUAL = Path(__file__).resolve().parent
RAIZ = DIRETORIO_ATUAL.parent
TMPDIR = RAIZ / "tmp"                        # base intermediaria (entrada)
OUTDIR = RAIZ / "output"                     # saidas finais (tabelas/figuras)
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")
base = base.assign(ipca_lag1=base["ipca"].shift(1)).dropna()
base["mes"] = base.index.month
base["tendencia"] = np.arange(len(base))

FORMULA = "ipca ~ desemprego + ipca_lag1 + exp_ipca_prox"

# estimo as 4 especificacoes
m_base = smf.ols(FORMULA, data=base).fit()
m_sazonal = smf.ols(FORMULA + " + C(mes)", data=base).fit()
fora_covid = ~((base.index >= "2020-03-01") & (base.index <= "2021-06-01"))
m_sem_covid = smf.ols(FORMULA, data=base[fora_covid]).fit()
m_tendencia = smf.ols(FORMULA + " + tendencia", data=base).fit()

modelos = {
    "Base": m_base,
    "+ Sazonal": m_sazonal,
    "Sem COVID": m_sem_covid,
    "+ Tendência": m_tendencia,
}

# Breusch-Godfrey(12) por especificacao (so pra registrar o efeito da sazonalidade)
bg_p = {nome: acorr_breusch_godfrey(mod, nlags=12)[1] for nome, mod in modelos.items()}

# tabela so com os coeficientes-chave (as 11 dummies de mes ficam ocultas)
sg = Stargazer(list(modelos.values()))
sg.dependent_variable_name("IPCA mensal")
sg.title("Robustez do modelo dinâmico (coeficientes-chave)")
sg.custom_columns(list(modelos.keys()), [1, 1, 1, 1])
sg.rename_covariates({
    "desemprego": "Desemprego $u_t$",
    "ipca_lag1": r"Inflação defasada $\pi_{t-1}$",
    "exp_ipca_prox": r"Expectativa $E_t[\pi_{t+1}]$",
    "tendencia": "Tendência linear",
})
sg.covariate_order(["desemprego", "ipca_lag1", "exp_ipca_prox", "tendencia"])
sg.add_line("Dummies sazonais", ["Não", "Sim", "Não", "Não"])
sg.add_line("Breusch--Godfrey(12) $p$", [f"{bg_p[n]:.2g}" for n in modelos])
(OUTDIR / "q2_tab_robustez.tex").write_text(sg.render_latex(), encoding="utf-8")

# numeros-chave pra interpretacao (robustez)
print("=== Robustez do modelo dinamico (coeficientes-chave) ===")
print(f"  {'especificacao':14s} {'n':>4s} {'u (p)':>16s} {'gamma':>8s} {'delta':>8s} {'R2':>6s} {'BG p':>9s}")
for nome, mod in modelos.items():
    print(f"  {nome:14s} {int(mod.nobs):>4d} "
          f"{mod.params['desemprego']:>8.4f} (p={mod.pvalues['desemprego']:.2f}) "
          f"{mod.params['ipca_lag1']:>8.3f} {mod.params['exp_ipca_prox']:>8.3f} "
          f"{mod.rsquared:>6.3f} {bg_p[nome]:>9.2g}")
print("\n  Leitura: em todas as variantes, inercia e expectativa seguem dominando e o")
print("  desemprego segue insignificante. As dummies sazonais sobem o R2 e reduzem (mas")
print("  nao zeram) a autocorrelacao -> parte do residuo do q2_5 era sazonalidade do IPCA.")
print("\nArquivo salvo em output/: q2_tab_robustez.tex")

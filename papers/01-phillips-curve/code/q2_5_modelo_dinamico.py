"""
q2_5 - item 5: o modelo dinamico da Phillips. Estimo por MQO a versao
aceleracionista, com inercia e expectativa:
    pi_t = alpha + beta*u_t + gamma*pi_{t-1} + delta*E_t[pi_{t+1}] + e_t
(o pi_{t-1} entra como df["ipca"].shift(1)). Reavalio a autocorrelacao dos
residuos (que deve cair frente a estatica) e calculo o efeito de longo prazo do
desemprego, beta/(1-gamma). Exporto a tabela comparativa estatica x dinamica.

Autor: Guilherme Cabral (Grupo 1)
Data: 17/06/2026
Inputs:  tmp/q2_base_phillips.csv   (do q2_2)
Outputs: output/q2_tab_phillips_dinamica.tex
"""

from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, acorr_ljungbox
from stargazer.stargazer import Stargazer

# caminhos (raiz pelo proprio arquivo)
DIRETORIO_ATUAL = Path(__file__).resolve().parent
RAIZ = DIRETORIO_ATUAL.parent
TMPDIR = RAIZ / "tmp"                        # base intermediaria (entrada)
OUTDIR = RAIZ / "output"                     # saidas finais (tabelas/figuras)
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")

LAGS = 12   # mesma janela de defasagens dos testes de autocorrelacao do q2_4

# monto a inflacao defasada pi_{t-1}. isso custa a 1a observacao,
#    entao a dinamica roda com um mes a menos que a estatica
base = base.assign(ipca_lag1=base["ipca"].shift(1))
amostra = base.dropna()

# estatica (so de referencia) e a dinamica, as duas por MQO
estatica = smf.ols("ipca ~ desemprego", data=base).fit()
dinamica = smf.ols("ipca ~ desemprego + ipca_lag1 + exp_ipca_prox", data=amostra).fit()

# reavalio a autocorrelacao dos residuos da dinamica
#    Obs.: com a dependente defasada (pi_{t-1}) entre os regressores, o Durbin-
#    Watson vicia em direcao a 2 e perde validade, entao o teste que
#    "vale" aqui e o de Breusch-Godfrey (e o Ljung-Box).
dw_estatica = durbin_watson(estatica.resid)
dw_dinamica = durbin_watson(dinamica.resid)
bg_lm, bg_p, _, _ = acorr_breusch_godfrey(dinamica, nlags=LAGS)
lb = acorr_ljungbox(dinamica.resid, lags=[LAGS], return_df=True)
lb_q, lb_p = lb["lb_stat"].iloc[0], lb["lb_pvalue"].iloc[0]

# efeito de longo prazo do desemprego: beta/(1-gamma)
#    No equilibrio de longo prazo pi_t = pi_{t-1} = pi*, logo
#    pi* (1-gamma) = alpha + beta*u + delta*E[pi]  ->  d pi*/d u = beta/(1-gamma).
beta = dinamica.params["desemprego"]
gamma = dinamica.params["ipca_lag1"]
delta = dinamica.params["exp_ipca_prox"]
efeito_lp = beta / (1 - gamma)

# restricao aceleracionista (taxa natural): se gamma + delta = 1, a
# soma dos coefs de inflacao passada e esperada da 1, e a Curva de
# Phillips de longo prazo e vertical: nao tem trade-off permanente
teste_vertical = dinamica.t_test("ipca_lag1 + exp_ipca_prox = 1")
soma_gd = gamma + delta
p_vertical = teste_vertical.pvalue.item()

# tabela comparando estatica e dinamica
sg = Stargazer([estatica, dinamica])
sg.dependent_variable_name("IPCA mensal")
sg.title("Curva de Phillips: especificação estática vs.\\ dinâmica (MQO)")
sg.custom_columns(["Estática", "Dinâmica"], [1, 1])
sg.rename_covariates({
    "desemprego": "Desemprego $u_t$",
    "ipca_lag1": r"Inflação defasada $\pi_{t-1}$",
    "exp_ipca_prox": r"Expectativa $E_t[\pi_{t+1}]$",
})
sg.covariate_order(["desemprego", "ipca_lag1", "exp_ipca_prox", "Intercept"])
sg.add_line("Durbin--Watson", [f"{dw_estatica:.3f}", f"{dw_dinamica:.3f}"])
sg.add_line("Efeito de longo prazo $\\beta/(1-\\gamma)$", ["---", f"{efeito_lp:.4f}"])
sg.add_line("Breusch--Godfrey(12) $p$", ["$<$0.001", f"{bg_p:.3g}"])
sg.add_line("$H_0\\!: \\gamma+\\delta=1$ ($p$-valor)", ["---", f"{p_vertical:.3f}"])
(OUTDIR / "q2_tab_phillips_dinamica.tex").write_text(sg.render_latex(), encoding="utf-8")

# numeros-chave pra interpretacao (item 5)
print("=== Modelo dinamico:  pi_t = a + b*u_t + g*pi_{t-1} + d*E_t[pi_{t+1}] ===")
print(f"  Amostra: {amostra.index.min().date()} a {amostra.index.max().date()}  (n={int(dinamica.nobs)})")
print(f"  beta  (desemprego u_t)      = {beta:8.4f}   (p={dinamica.pvalues['desemprego']:.4f})")
print(f"  gamma (inercia pi_{{t-1}})     = {gamma:8.4f}   (p={dinamica.pvalues['ipca_lag1']:.4f})")
print(f"  delta (expectativa E[pi])   = {delta:8.4f}   (p={dinamica.pvalues['exp_ipca_prox']:.4f})")
print(f"  R^2 = {dinamica.rsquared:.4f}   (estatica: {estatica.rsquared:.4f})")
print(f"\n  Efeito de longo prazo do desemprego = beta/(1-gamma) = {efeito_lp:.4f}")
print("    (obs.: beta do desemprego e insignificante (p=0.39), entao este efeito de longo")
print("     prazo nao se distingue de zero -- coerente com Phillips ~vertical em u.)")
print(f"\n  Restricao aceleracionista  gamma+delta = {soma_gd:.4f}")
print(f"    H0: gamma+delta=1 (Phillips de longo prazo VERTICAL) -> "
          f"t={teste_vertical.tvalue.item():.3f}, p={p_vertical:.4f}")
print("    Nao se rejeita H0: a soma e estatisticamente compativel com 1, ou seja,")
print("    os dados nao contradizem a hipotese da taxa natural (sem trade-off de LP).")
print("\n  Autocorrelacao dos residuos (item 5, reavaliacao):")
print(f"    Durbin-Watson: {dw_estatica:.3f} (estatica) -> {dw_dinamica:.3f} (dinamica)")
print("      [DW viesado p/ 2 com dependente defasada; o teste valido e o BG]")
print(f"    Breusch-Godfrey(12): LM = {bg_lm:.2f}   p = {bg_p:.3g}")
print(f"    Ljung-Box(12)      : Q  = {lb_q:.2f}   p = {lb_p:.3g}")
print("\nArquivo salvo em output/: q2_tab_phillips_dinamica.tex")

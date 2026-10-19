"""
q2_3 - itens 1 e 2 da Questao 2.
 (1) ploto as 3 series no tempo (IPCA, desemprego, expectativa) e salvo as figuras.
 (2) estimo a Phillips ESTATICA por MQO (pi_t = alpha + beta*u_t + e_t) com o
     statsmodels, exporto a tabela em .tex e imprimo os numeros que uso na
     redacao (sinal e tamanho do beta, R2, Durbin-Watson).

Autor: Guilherme Cabral (Grupo 1)
Data: 20/06/2026
Inputs:  tmp/q2_base_phillips.csv   (do q2_2)
Outputs: output/q2_fig_series.pdf, output/q2_fig_phillips_scatter.pdf,
         output/q2_tab_phillips_estatica.tex

Figuras em PDF vetorial pro LaTeX, num estilo sobrio (titulo embutido, virgula
decimal e nota de fonte do BCB).
"""

from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")                       # backend sem tela (salva em arquivo)
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import statsmodels.formula.api as smf
from statsmodels.stats.stattools import durbin_watson
from stargazer.stargazer import Stargazer

# caminhos (raiz pelo proprio arquivo)
DIRETORIO_ATUAL = Path(__file__).resolve().parent
RAIZ = DIRETORIO_ATUAL.parent
TMPDIR = RAIZ / "tmp"                        # base intermediaria (entrada)
OUTDIR = RAIZ / "output"                     # figuras e tabelas (saidas finais)
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")

# estilo das figuras (versao final pro LaTeX): sobrio, serifado pra casar
# com a fonte do LaTeX, grade leve, virgula decimal e nota de fonte.
# saida em PDF vetorial; o titulo fica embutido na figura
plt.rcParams.update({
    "font.family": "serif", "mathtext.fontset": "cm",
    "axes.titlesize": 12, "axes.labelsize": 10.5, "axes.linewidth": 0.8,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9.5,
    "axes.grid": True, "grid.color": "0.85", "grid.linewidth": 0.6,
    "axes.axisbelow": True,
})
COR = {"ipca": "#1f4e79", "desemp": "#9c2b2b", "exp": "#2e6f3e"}
FONTE_BCB = ("Fonte: BCB — SGS (IPCA 433; desocupação PNADC 24369) e "
             "Expectativas/Focus. Elaboração própria.")
def _virgula(casas):
    return FuncFormatter(lambda x, _: (f"%.{casas}f" % x).replace(".", ","))
def _nota_fonte(figura, texto):
    figura.text(0.012, 0.008, texto, ha="left", va="bottom", fontsize=7.2,
                color="0.35", style="italic")

# (1) as 3 series no tempo, em 3 paineis (escalas diferentes)
fig, eixos = plt.subplots(3, 1, figsize=(7.4, 6.2), sharex=True)
fig.suptitle("Curva de Phillips brasileira — séries mensais (2012–2026)",
             y=0.975, fontsize=12.5)
paineis = [
    ("ipca", "IPCA\n(% a.m.)", COR["ipca"]),
    ("desemprego", "Desemprego\nPNADC (%)", COR["desemp"]),
    ("exp_ipca_prox", "Expectativa\nFocus $E_t[\\pi_{t+1}]$ (%)", COR["exp"]),
]
for ax, (col, rotulo, cor) in zip(eixos, paineis):
    ax.plot(base.index, base[col], color=cor, lw=1.3)
    ax.set_ylabel(rotulo, fontsize=9.5)
    ax.yaxis.set_major_formatter(_virgula(1))
    ax.margins(x=0.01)
eixos[-1].set_xlabel("Mês")
fig.subplots_adjust(left=0.135, right=0.985, top=0.93, bottom=0.085, hspace=0.12)
_nota_fonte(fig, FONTE_BCB)
fig.savefig(OUTDIR / "q2_fig_series.pdf")
plt.close(fig)

# (2) Phillips estatica: pi_t = alpha + beta*u_t + e_t.
modelo = smf.ols("ipca ~ desemprego", data=base).fit()
dw = durbin_watson(modelo.resid)
beta = modelo.params["desemprego"]
pval = modelo.pvalues["desemprego"]

# dispersao com a reta ajustada, pra enxergar o trade-off
fig2, ax = plt.subplots(figsize=(7.4, 5.0))
ax.scatter(base["desemprego"], base["ipca"], s=26, alpha=0.55,
           color=COR["ipca"], edgecolor="white", linewidth=0.4)
xs = base["desemprego"].sort_values()
alpha0 = modelo.params["Intercept"]
sinal = "−" if beta < 0 else "+"                     # evita o "+ -0,0024" duplicado
rotulo_reta = (f"MQO: $\\pi = {alpha0:.3f}".replace(".", ",")
               + f" {sinal} {abs(beta):.4f}".replace(".", ",") + "\\,u$")
ax.plot(xs, alpha0 + beta * xs, color=COR["desemp"], lw=2.2, label=rotulo_reta)
ax.set_xlabel("Taxa de desemprego (%)")
ax.set_ylabel("IPCA (% a.m.)")
ax.set_title("Curva de Phillips estática: inflação × desemprego (2012–2026)")
ax.xaxis.set_major_formatter(_virgula(0))
ax.yaxis.set_major_formatter(_virgula(1))
ax.legend(loc="upper left", frameon=True, framealpha=0.9)
ax.annotate(f"$R^2 \\approx {modelo.rsquared:.3f}$".replace(".", ",")
            + f";  $p_\\beta = {pval:.2f}$".replace(".", ","),
            xy=(0.985, 0.04), xycoords="axes fraction", ha="right",
            fontsize=9, color="0.3")
_nota_fonte(fig2, FONTE_BCB)
fig2.subplots_adjust(left=0.09, right=0.985, top=0.92, bottom=0.12)
fig2.savefig(OUTDIR / "q2_fig_phillips_scatter.pdf")
plt.close(fig2)

# tabela LaTeX via stargazer (rotulos batendo com os do q2_5/q2_6)
sg = Stargazer([modelo])
sg.dependent_variable_name("IPCA mensal")
sg.title("Curva de Phillips estática — MQO: $\\pi_t = \\alpha + \\beta\\,u_t + \\varepsilon_t$")
sg.custom_columns(["IPCA mensal ($\\pi_t$)"], [1])
sg.rename_covariates({"desemprego": "Desemprego $u_t$"})
sg.covariate_order(["desemprego", "Intercept"])
sg.add_line("Durbin-Watson", [f"{dw:.3f}"])
with open(OUTDIR / "q2_tab_phillips_estatica.tex", "w", encoding="utf-8") as f:
    f.write(sg.render_latex())

# numeros-chave pra interpretacao (item 2)
print("=== Phillips estática:  pi_t = alpha + beta*u_t + e_t ===")
print(f"  Amostra: {base.index.min().date()} a {base.index.max().date()}  (n={int(modelo.nobs)})")
print(f"  beta (desemprego) = {beta:.4f}   (p-valor = {pval:.4f})")
print(f"  alpha (intercepto)= {modelo.params['Intercept']:.4f}")
print(f"  R^2 = {modelo.rsquared:.4f}    Durbin-Watson = {dw:.3f}")
if pval >= 0.10:
    leitura = (f"{'negativo' if beta < 0 else 'positivo'}, mas ESTATISTICAMENTE NULO "
               f"(p={pval:.2f}, R2~0) -> sem trade-off estatico visivel")
else:
    leitura = ("negativo e significante (trade-off como na teoria)" if beta < 0
               else "positivo e significante (contraria o trade-off simples)")
print(f"  -> beta: {leitura}")
print("\nArquivos salvos em output/: q2_fig_series.pdf, q2_fig_phillips_scatter.pdf, q2_tab_phillips_estatica.tex")

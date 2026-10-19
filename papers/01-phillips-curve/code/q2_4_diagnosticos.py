"""
q2_4 - itens 3 e 4 da Questao 2.
 (3) regressao espuria: testo a estacionariedade das 3 series com ADF (H0: raiz
     unitaria) e KPSS (H0: estacionaria), em nivel e em 1a diferenca, e discuto
     o risco de espuria na estatica (reestimo em diferenca so pra ilustrar a
     mitigacao).
 (4) autocorrelacao: nos residuos da estatica rodo Durbin-Watson, Breusch-Godfrey
     e Ljung-Box, e ploto a FAC dos residuos.
No fim exporto as tabelas .tex e a figura, e imprimo os numeros-chave.

Autor: Guilherme Cabral (Grupo 1)
Data: 17/06/2026
Inputs:  tmp/q2_base_phillips.csv   (do q2_2)
Outputs: output/q2_tab_estacionariedade.tex, output/q2_tab_autocorrelacao.tex,
         output/q2_fig_acf_residuos.pdf

Figura em PDF vetorial pro LaTeX, mesmo estilo sobrio dos outros scripts.
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                       # backend sem tela (salva em arquivo)
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import statsmodels.formula.api as smf
from statsmodels.tsa.stattools import adfuller, kpss, acf
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, acorr_ljungbox

# caminhos (raiz pelo proprio arquivo)
DIRETORIO_ATUAL = Path(__file__).resolve().parent
RAIZ = DIRETORIO_ATUAL.parent
TMPDIR = RAIZ / "tmp"                        # base intermediaria (entrada)
OUTDIR = RAIZ / "output"                     # saidas finais (tabelas/figuras)
OUTDIR.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(TMPDIR / "q2_base_phillips.csv", parse_dates=["data"]).set_index("data")

# estilo da figura (versao final pro LaTeX): sobrio, serifado, grade
# leve, virgula decimal e nota de fonte; saida em PDF vetorial
plt.rcParams.update({
    "font.family": "serif", "mathtext.fontset": "cm",
    "axes.titlesize": 12, "axes.labelsize": 10.5, "axes.linewidth": 0.8,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.grid": True, "grid.color": "0.85", "grid.linewidth": 0.6,
    "axes.axisbelow": True,
})
COR_ACF = "#1f4e79"
def _virgula(casas):
    return FuncFormatter(lambda x, _: (f"%.{casas}f" % x).replace(".", ","))
def _nota_fonte(figura, texto):
    figura.text(0.012, 0.008, texto, ha="left", va="bottom", fontsize=7.2,
                color="0.35", style="italic")

# defasagens dos testes de autocorrelacao: 12 meses = 1 ano, escolha
# natural pra dado mensal (capta tambem a sazonalidade anual)
LAGS = 12

# Rotulos prontos para LaTeX (o '%' precisa vir escapado como \% nas tabelas).
ROTULOS = {
    "ipca": r"IPCA (\% a.m.)",
    "desemprego": r"Desemprego (\%)",
    "exp_ipca_prox": r"Expectativa $E_t[\pi_{t+1}]$ (\%)",
}

# (3) estacionariedade: ADF e KPSS se complementam, com H0 opostas
#     - ADF  (H0: tem raiz unitaria);  rejeito (p baixo) => estacionaria.
#     - KPSS (H0: e estacionaria);     rejeito (p baixo) => nao-estacionaria.
#     uso os dois pra nao tirar conclusao apressada (cada um tem pouca potencia)
def roda_adf(serie):
    estatistica, p_valor, defasagens, *_ = adfuller(serie.dropna(), regression="c", autolag="AIC")
    return estatistica, p_valor

def roda_kpss(serie):
    # KPSS emite InterpolationWarning quando o p-valor cai fora da tabela (=> p
    # esta no limite, ">0.10" ou "<0.01"); a supressao aqui e so de ruido.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InterpolationWarning)
        estatistica, p_valor, *_ = kpss(serie.dropna(), regression="c", nlags="auto")
    return estatistica, p_valor

def leitura_conjunta(p_adf, p_kpss):
    estac_adf = p_adf < 0.05            # ADF rejeita raiz unitaria
    estac_kpss = p_kpss >= 0.05         # KPSS nao rejeita estacionariedade
    if estac_adf and estac_kpss:
        return "Estacionária"
    if (not estac_adf) and (not estac_kpss):
        return "Não-estacionária"
    return "Persistente (evid.\\ mista)"

def fmt_kpss_p(p):
    # statsmodels limita o p do KPSS a [0.01, 0.10]; sinalizo o teto/piso.
    if p >= 0.10:
        return r"$>$0.10"
    if p <= 0.01:
        return r"$<$0.01"
    return f"{p:.3f}"

adf_nivel = {c: roda_adf(base[c]) for c in ROTULOS}
kpss_nivel = {c: roda_kpss(base[c]) for c in ROTULOS}
adf_diff = {c: roda_adf(base[c].diff()) for c in ["ipca", "desemprego"]}

# (4) autocorrelacao nos residuos da estatica (pi_t = a + b*u_t + e_t)
estatica = smf.ols("ipca ~ desemprego", data=base).fit()
residuos = estatica.resid

dw = durbin_watson(residuos)
bg_lm, bg_p, _, _ = acorr_breusch_godfrey(estatica, nlags=LAGS)
lb = acorr_ljungbox(residuos, lags=[LAGS], return_df=True)
lb_q, lb_p = lb["lb_stat"].iloc[0], lb["lb_pvalue"].iloc[0]

# mitigacao por diferencas: reestimo a estatica em 1a diferenca
base_diff = base.assign(d_ipca=base["ipca"].diff(), d_desemprego=base["desemprego"].diff()).dropna()
estatica_diff = smf.ols("d_ipca ~ d_desemprego", data=base_diff).fit()

# FAC dos residuos: mostra a persistencia que os testes pegam
# Banda de confianca de Bartlett (alpha=0.05) que alarga com a defasagem.
NLAGS_FAC = 24
fac_vals, fac_ci = acf(residuos, nlags=NLAGS_FAC, alpha=0.05, fft=False)
lags_fac = np.arange(NLAGS_FAC + 1)
banda = fac_ci[:, 1] - fac_vals                 # metade do IC (Bartlett)
fig, ax = plt.subplots(figsize=(7.4, 4.3))
ax.fill_between(lags_fac, -banda, banda, color=COR_ACF, alpha=0.13, lw=0)
ax.vlines(lags_fac, 0, fac_vals, color=COR_ACF, lw=1.4)
ax.scatter(lags_fac, fac_vals, s=22, color=COR_ACF, zorder=3)
ax.axhline(0, color="0.4", lw=0.8)
ax.set_title("FAC dos resíduos da Phillips estática")
ax.set_xlabel("Defasagem (meses)")
ax.set_ylabel("Autocorrelação")
ax.yaxis.set_major_formatter(_virgula(2))
ax.set_xlim(-0.5, NLAGS_FAC + 0.5)
ax.set_ylim(-0.4, 1.02)
rho1 = fac_vals[1]                              # autocorrelacao na 1a defasagem
ax.annotate(f"$\\hat\\rho_1 \\approx {rho1:.3f}$".replace(".", ","),
            xy=(1, rho1), xytext=(3.2, 0.74), fontsize=9, color="0.25",
            arrowprops=dict(arrowstyle="->", color="0.5", lw=0.9))
_nota_fonte(fig, "Elaboração própria a partir dos resíduos da regressão estática.")
fig.subplots_adjust(left=0.10, right=0.985, top=0.90, bottom=0.135)
fig.savefig(OUTDIR / "q2_fig_acf_residuos.pdf")
plt.close(fig)

# tabela 1 (item 3): ADF + KPSS em nivel, e ADF na 1a diferenca
linhas = []
for col, rot in ROTULOS.items():
    a_est, a_p = adf_nivel[col]
    k_est, k_p = kpss_nivel[col]
    linhas.append(f"{rot} & {a_est:.2f} & {a_p:.3f} & {k_est:.2f} & {fmt_kpss_p(k_p)} "
                  f"& {leitura_conjunta(a_p, k_p)} \\\\")
linhas.append("\\midrule")
linhas.append("\\multicolumn{6}{l}{\\textit{Em primeira diferença (apenas ADF):}} \\\\")
for col in ["ipca", "desemprego"]:
    a_est, a_p = adf_diff[col]
    rot = "$\\Delta$ " + ROTULOS[col]
    concl = "Estacionária" if a_p < 0.05 else "Estac.\\ a 10\\%" if a_p < 0.10 else "Não-estac."
    linhas.append(f"{rot} & {a_est:.2f} & {a_p:.3f} & --- & --- & {concl} \\\\")

tab_adf = (
    "\\begin{table}[htbp]\n\\centering\n"
    "\\caption{Estacionariedade: ADF ($H_0$: raiz unitária) e KPSS "
    "($H_0$: estacionária)}\n\\label{tab:adf}\n"
    "\\begin{tabular}{lcccccc}\n\\toprule\n"
    "& \\multicolumn{2}{c}{ADF} & \\multicolumn{2}{c}{KPSS} & \\\\\n"
    "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n"
    "Série & Estat. & $p$ & Estat. & $p$ & Conclusão (5\\%) \\\\\n"
    "\\midrule\n" + "\n".join(linhas) + "\n"
    "\\bottomrule\n\\end{tabular}\n\\end{table}\n"
)
(OUTDIR / "q2_tab_estacionariedade.tex").write_text(tab_adf, encoding="utf-8")

# tabela 2 (item 4): testes de autocorrelacao dos residuos
tab_auto = (
    "\\begin{table}[htbp]\n\\centering\n"
    "\\caption{Autocorrelação dos resíduos da Phillips estática "
    "($H_0$: ausência de autocorrelação)}\n\\label{tab:autocorr}\n"
    "\\begin{tabular}{lccc}\n\\toprule\n"
    "Teste & Estatística & $p$-valor & Conclusão (5\\%) \\\\\n"
    "\\midrule\n"
    f"Durbin--Watson & {dw:.3f} & --- & Autocorrelação positiva \\\\\n"
    f"Breusch--Godfrey ({LAGS} defas.) & {bg_lm:.2f} & {bg_p:.3g} & Rejeita $H_0$ \\\\\n"
    f"Ljung--Box ({LAGS} defas.) & {lb_q:.2f} & {lb_p:.3g} & Rejeita $H_0$ \\\\\n"
    "\\bottomrule\n\\end{tabular}\n\\end{table}\n"
)
(OUTDIR / "q2_tab_autocorrelacao.tex").write_text(tab_auto, encoding="utf-8")

# numeros-chave pra interpretacao (itens 3 e 4)
print("=== Item 3: estacionariedade (ADF: H0=raiz unit.; KPSS: H0=estacionaria) ===")
for col in ROTULOS:
    a_est, a_p = adf_nivel[col]; k_est, k_p = kpss_nivel[col]
    print(f"  {col:14s} ADF={a_est:7.3f} (p={a_p:.3f}) | KPSS={k_est:.3f} (p={'>0.10' if k_p>=0.10 else f'{k_p:.3f}'})"
          f"  -> {leitura_conjunta(a_p, k_p).replace(chr(92),'')}")
print("  primeira diferenca (ADF):")
for col in ["ipca", "desemprego"]:
    a_est, a_p = adf_diff[col]
    print(f"  d.{col:12s} ADF={a_est:7.3f}  p={a_p:.3f}")
print(f"  Phillips estatica em diferencas: beta(d.desemprego) = {estatica_diff.params['d_desemprego']:.4f} "
      f"(p={estatica_diff.pvalues['d_desemprego']:.3f}), R2={estatica_diff.rsquared:.4f}")
print("  -> IPCA estacionario nos dois testes; desemprego/expectativa sao PERSISTENTES com")
print("     evidencia mista (ADF nao rejeita raiz unit.; KPSS nao rejeita estacionariedade).")

print("\n=== Item 4: autocorrelacao dos residuos da estatica (H0 = sem autocorrelacao) ===")
print(f"  Durbin-Watson           = {dw:.3f}   (~2 = sem autocorr.; <2 = positiva)")
print(f"  Breusch-Godfrey({LAGS})    : LM = {bg_lm:.2f}   p = {bg_p:.3g}")
print(f"  Ljung-Box({LAGS})          : Q  = {lb_q:.2f}   p = {lb_p:.3g}")
print("  -> Os tres apontam forte autocorrelacao: a estatica esta mal especificada")
print("     (faltam inercia e expectativas), o que motiva o modelo dinamico (q2_5).")
print("  Obs. (item 3): o sintoma classico de espuria (R2 alto + DW baixo) NAO aparece:")
print("     o R2 da estatica e ~0 porque o IPCA e estacionario (I(0)); o DW baixo reflete")
print("     dinamica omitida, nao uma regressao de tendencia contra tendencia.")
print("\nArquivos salvos em output/: q2_tab_estacionariedade.tex, q2_tab_autocorrelacao.tex, q2_fig_acf_residuos.pdf")

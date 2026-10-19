"""
q3_helpers - funcoes de apoio da Questao 3: formata numeros com virgula decimal,
monta as tabelas .tex (booktabs) a partir dos modelos do statsmodels e do
linearmodels, e define o estilo das figuras.

Autor: Guilherme Cabral (Grupo 1)
Data: 27/06/2026
"""
from __future__ import annotations
import numpy as np

FONTE = ("Fonte: Cornwell e Trumbull (1994), painel de 90 condados da Carolina do "
         "Norte (1981-1987), via wooldridge::crime4. Elaboracao propria.")

COR = {"azul": "#1f4e79", "vermelho": "#9c2b2b", "verde": "#2e6f3e",
       "cinza": "#555555", "laranja": "#b5651d"}

def num(x, casas=3):
    if x is None:
        return "--"
    try:
        if np.isnan(x):
            return "--"
    except TypeError:
        return "--"
    return f"{x:.{casas}f}".replace(".", ",")

def estrelas(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""

def pval(p, casas=4):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "--"
    minimo = 10 ** (-casas)
    if p < minimo:
        return ("$<$" + f"{minimo:.{casas}f}").replace(".", ",")
    return num(p, casas)

def extrai(res):
    # uniformiza os resultados de statsmodels (OLS) e linearmodels (PanelOLS)
    if hasattr(res, "bse"):
        return {"coef": res.params, "se": res.bse, "p": res.pvalues,
                "n": int(res.nobs), "r2": float(getattr(res, "rsquared", np.nan))}
    return {"coef": res.params, "se": res.std_errors, "p": res.pvalues,
            "n": int(res.nobs), "r2": float(res.rsquared)}

def _cel(ext, var, casas):
    if var not in ext["coef"].index:
        return None
    b, s, p = ext["coef"][var], ext["se"][var], ext["p"][var]
    return num(b, casas) + estrelas(p), "(" + num(s, casas) + ")"

def tabela_regressao(path, modelos, vars_label, rodape, caption, label,
                     casas=3, nota=None, dep="ln(taxa de crime)"):
    ncol = len(modelos)
    L = [r"\begin{table}[htbp]\centering",
         rf"\caption{{{caption}}}\label{{{label}}}", r"\small",
         rf"\begin{{tabular}}{{l{'c'*ncol}}}", r"\toprule",
         " & " + " & ".join(rf"\textbf{{{t}}}" for t, _ in modelos) + r" \\",
         " & " + " & ".join(f"({i+1})" for i in range(ncol)) + r" \\",
         r"\midrule"]
    for var, rot in vars_label:
        lb, ls = [rot], [""]
        for _, ext in modelos:
            c = _cel(ext, var, casas)
            lb.append(c[0] if c else "")
            ls.append(c[1] if c else "")
        L.append(" & ".join(lb) + r" \\")
        L.append(" & ".join(ls) + r" \\")
    L.append(r"\midrule")
    for rot, vals in rodape:
        L.append(rot + " & " + " & ".join(str(v) for v in vals) + r" \\")
    L.append("N (obs.) & " + " & ".join(str(ext["n"]) for _, ext in modelos) + r" \\")
    L.append(r"$R^2$ & " + " & ".join(num(ext["r2"], 3) for _, ext in modelos) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    if nota is None:
        nota = ("Erros-padrao entre parenteses. *** p$<$0,01; ** p$<$0,05; "
                f"* p$<$0,10. Variavel dependente: {dep}.")
    L.append(rf"\par\vspace{{2pt}}{{\footnotesize\itshape {nota}}}")
    L.append(r"\end{table}")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")

def tabela_descritivas(path, df, vars_label, caption, label, casas=3):
    L = [r"\begin{table}[htbp]\centering",
         rf"\caption{{{caption}}}\label{{{label}}}",
         r"\small", r"\begin{tabular}{lrrrrr}", r"\toprule",
         r"Variavel & Obs. & Media & Desv.-padrao & Min. & Max. \\", r"\midrule"]
    for var, rot in vars_label:
        s = df[var]
        L.append(f"{rot} & {int(s.count())} & {num(s.mean(),casas)} & "
                 f"{num(s.std(),casas)} & {num(s.min(),casas)} & {num(s.max(),casas)} \\\\")
    L += [r"\bottomrule", r"\end{tabular}",
          rf"\par\vspace{{2pt}}{{\footnotesize\itshape {FONTE}}}", r"\end{table}"]
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")

def tabela_testes_het(path, bp, white, caption, label):
    L = [r"\begin{table}[htbp]\centering",
         rf"\caption{{{caption}}}\label{{{label}}}",
         r"\begin{tabular}{lccc}", r"\toprule",
         r"Teste & Estatistica LM & g.l. & p-valor \\", r"\midrule",
         rf"Breusch--Pagan & {num(bp['stat'],2)} & {bp['df']} & {pval(bp['p'])} \\",
         rf"White & {num(white['stat'],2)} & {white['df']} & {pval(white['p'])} \\",
         r"\bottomrule", r"\end{tabular}",
         r"\par\vspace{2pt}{\footnotesize\itshape $H_0$: homocedasticidade. "
         r"Estatistica LM $=n\cdot R^2$ da regressao auxiliar. Rejeitar $H_0$ "
         r"indica heterocedasticidade.}",
         r"\end{table}"]
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")

def estilo_figuras():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "serif", "mathtext.fontset": "cm",
        "axes.titlesize": 12, "axes.labelsize": 10.5, "axes.linewidth": 0.8,
        "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9.5,
        "axes.grid": True, "grid.color": "0.85", "grid.linewidth": 0.6,
        "axes.axisbelow": True,
    })

def nota_fonte(fig, texto=FONTE):
    fig.text(0.012, 0.008, texto, ha="left", va="bottom",
             fontsize=7.0, color="0.35", style="italic")

# especificacao usada em todos os scripts
DETERRENCIA = ["lprbarr", "lprbconv", "lprbpris", "lavgsen", "lpolpc"]
CONT = DETERRENCIA + ["ldensity", "lpctymle", "ltaxpc", "lmix", "lwcon", "pctmin80"]
DUM = ["west", "central", "urban"]
RHS_POOLED = CONT + DUM
RHS_FE = ["lprbarr", "lprbconv", "lprbpris", "lavgsen", "lpolpc",
          "ltaxpc", "lmix", "lwcon"]
ROT = {
    "lprbarr":  r"ln(prob.\ pris\~ao) $\beta_1$",
    "lpolpc":   r"ln(pol\'icia p.c.) $\beta_2$",
    "lprbconv": r"ln(prob.\ condena\c{c}\~ao)",
    "lprbpris": r"ln(prob.\ encarc.)",
    "lavgsen":  r"ln(senten\c{c}a m\'edia)",
}
VARS_DESCR = [
    ("crmrte",   "Taxa de crime (crimes/pessoa)"),
    ("prbarr",   "Prob.\\ de pris\\~ao"),
    ("prbconv",  "Prob.\\ de condena\\c{c}\\~ao"),
    ("prbpris",  "Prob.\\ de encarceramento"),
    ("avgsen",   "Senten\\c{c}a m\\'edia (dias)"),
    ("polpc",    "Pol\\'icia per capita"),
    ("density",  "Densidade (hab./mi$^2$)"),
    ("taxpc",    "Receita tribut\\'aria p.c."),
    ("pctymle",  "\\% homens jovens"),
    ("pctmin80", "\\% minoria (1980)"),
    ("mix",      "Raz\\~ao crimes graves/leves"),
]

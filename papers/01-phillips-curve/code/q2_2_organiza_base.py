"""
q2_2 - junta as 3 series cruas (do q2_1) numa base mensal unica, alinhada por
data e pronta pra estimar a Phillips. O trabalhoso aqui e o Focus: tem varias
leituras por mes, entao reduzo pra uma so - a mediana da ultima pesquisa do mes
t que aponta pro mes t+1 (a expectativa que "valia" quando a inflacao do mes se
formou). No fim corto pra janela comum das tres series.

Autor: Guilherme Cabral (Grupo 1)
Data: 16/06/2026
Inputs:  tmp/q2_ipca.csv, tmp/q2_desemprego.csv, tmp/q2_focus_mensal.csv
Outputs: tmp/q2_base_phillips.csv  (data, ipca, desemprego, exp_ipca_prox)

Decisoes de modelagem (combinadas com o grupo):
 - inflacao = IPCA mensal (% a.m.), casando com a equacao mensal.
 - expectativa = mediana do Focus pro mes t+1, na ultima pesquisa do mes t.
 - janela = intersecao das tres series (limitada pela PNADC, 2012-03 em diante).
"""

from pathlib import Path
import pandas as pd

# caminhos (raiz pelo proprio arquivo)
DIRETORIO_ATUAL = Path(__file__).resolve().parent      # .../code
RAIZ = DIRETORIO_ATUAL.parent                          # raiz do projeto
TMPDIR = RAIZ / "tmp"
TMPDIR.mkdir(parents=True, exist_ok=True)

# IPCA e desemprego ja vem mensais e indexados por data
ipca = pd.read_csv(TMPDIR / "q2_ipca.csv", parse_dates=["Date"]).set_index("Date")
desemprego = pd.read_csv(TMPDIR / "q2_desemprego.csv", parse_dates=["Date"]).set_index("Date")

# jogo o indice pro 1o dia do mes pra garantir o alinhamento
ipca.index = ipca.index.to_period("M").to_timestamp()
desemprego.index = desemprego.index.to_period("M").to_timestamp()

# Focus -> uma observacao por mes de E_t[pi_{t+1}]
#    - 'Data'          = data da pesquisa (dentro do mes t)
#    - 'DataReferencia'= mes-alvo da expectativa (MM/AAAA)
#    pego ref == mes+1 e fico com a ultima pesquisa de cada mes t;
#    uso a mediana. indexo pelo mes t (quando a expectativa
#    foi formada) pra casar com pi_t na regressao
focus = pd.read_csv(TMPDIR / "q2_focus_mensal.csv")
focus["Data"] = pd.to_datetime(focus["Data"])
focus["ref"] = pd.to_datetime(focus["DataReferencia"], format="%m/%Y")
focus["mes_pesq"] = focus["Data"].dt.to_period("M")
focus["mes_ref"] = focus["ref"].dt.to_period("M")

um_mes_a_frente = focus[focus["mes_ref"] == (focus["mes_pesq"] + 1)]
ultima_leitura = um_mes_a_frente.sort_values("Data").groupby("mes_pesq").tail(1)

exp = (
    ultima_leitura.assign(data=ultima_leitura["mes_pesq"].dt.to_timestamp())
    .set_index("data")[["Mediana"]]
    .rename(columns={"Mediana": "exp_ipca_prox"})
)

# junta tudo num df mensal e corta pra janela comum (sem buracos)
base = (
    ipca.join(desemprego, how="outer")
    .join(exp, how="outer")
    .sort_index()
    .dropna()                       # so os meses que tem as 3 series
)
base.index.name = "data"

base.to_csv(TMPDIR / "q2_base_phillips.csv")

print("Base da Curva de Phillips montada.")
print(f"  Periodo: {base.index.min().date()} a {base.index.max().date()}  ({len(base)} meses)")
print(f"  Colunas: {list(base.columns)}")
print("\nPrimeiras linhas:")
print(base.head().to_string())
print("\nUltimas linhas:")
print(base.tail().to_string())
print(f"\nSalvo em: tmp/q2_base_phillips.csv")

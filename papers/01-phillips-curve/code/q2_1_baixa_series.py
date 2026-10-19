"""
q2_1 - baixa as 3 series da Questao 2 direto das APIs do BCB: IPCA mensal,
desemprego (PNAD Continua) e a expectativa de inflacao do Focus. Aqui eu so
baixo e salvo cada serie crua em tmp/; quem arruma e junta isso e o q2_2.

Autor: Guilherme Cabral (Grupo 1)
Data: 16/06/2026
Inputs:  nenhum (os dados vem das APIs do BCB: SGS e Expectativas/Olinda)
Outputs: tmp/q2_ipca.csv, tmp/q2_desemprego.csv, tmp/q2_focus_mensal.csv
"""

from pathlib import Path
import pandas as pd
from bcb import sgs, Expectativas

# caminhos: a raiz vem do proprio arquivo, entao roda em qualquer maquina
# (mesmo esquema que o _master.py usa)
DIRETORIO_ATUAL = Path(__file__).resolve().parent      # .../code
RAIZ = DIRETORIO_ATUAL.parent                          # raiz do projeto
TMPDIR = RAIZ / "tmp"
TMPDIR.mkdir(parents=True, exist_ok=True)

# a PNAD Continua so comeca em 2012, entao corto tudo a partir dai
DATA_INICIO = "2012-01-01"

# IPCA e desemprego PNADC, baixados juntos pelo SGS do BCB
# codigos do SGS:
#       433   = IPCA - variacao mensal (% a.m.)
#       24369 = Taxa de desocupacao - PNAD Continua (%)
print("Baixando IPCA (433) e desemprego (24369) do SGS...")
sgs_df = sgs.get({"ipca": 433, "desemprego": 24369}, start=DATA_INICIO)

ipca = sgs_df[["ipca"]].dropna()
desemprego = sgs_df[["desemprego"]].dropna()

ipca.to_csv(TMPDIR / "q2_ipca.csv")
desemprego.to_csv(TMPDIR / "q2_desemprego.csv")
print(f"  IPCA:       {len(ipca):>4} meses ({ipca.index.min().date()} a {ipca.index.max().date()})")
print(f"  Desemprego: {len(desemprego):>4} meses ({desemprego.index.min().date()} a {desemprego.index.max().date()})")

# expectativa de inflacao do Focus (mensal, pro IPCA)
# endpoint ExpectativaMercadoMensais (API de Expectativas/Olinda)
#    - Indicador  = 'IPCA'
#    - baseCalculo = 0  -> estatistica das respostas dos ultimos 30 dias
# guardo a mediana e a media, por data da pesquisa
# e por mes de referencia; o alinhamento mensal fica pro q2_2
print("Baixando expectativa Focus (IPCA mensal)...")
em = Expectativas()
ep = em.get_endpoint("ExpectativaMercadoMensais")
focus = (
    ep.query()
    .filter(ep.Indicador == "IPCA")
    .filter(ep.baseCalculo == 0)
    .filter(ep.Data >= DATA_INICIO)
    .select(ep.Indicador, ep.Data, ep.DataReferencia, ep.Mediana, ep.Media)
    .collect()
)
focus.to_csv(TMPDIR / "q2_focus_mensal.csv", index=False)
print(f"  Focus:      {len(focus):>4} linhas baixadas")

print("\nPronto! Series cruas salvas em tmp/ (q2_ipca.csv, q2_desemprego.csv, q2_focus_mensal.csv).")

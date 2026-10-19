# -*- coding: utf-8 -*-
# baixar_internet_2010.py — UPGRADE OPCIONAL (rodar na sua máquina, rede aberta).
# Objetivo: obter % de domicílios com acesso à internet por município (Censo 2010)
# para reintroduzir o eixo "internet" no estudo. NÃO roda no sandbox (SIDRA/BigQuery bloqueados).
# Fonte canônica: IBGE Censo 2010, variável V0220 (microcomputador com acesso à internet), amostra.
# Opção A (recomendada) — BigQuery/basedosdados (conta Google gratuita):
#   SELECT id_municipio AS municipio_id,
#          SUM(CASE WHEN v0220='1' THEN peso_amostral ELSE 0 END)/SUM(peso_amostral) AS internet_share
#   FROM `basedosdados.br_ibge_censo_demografico.microdados_domicilio_2010`
#   GROUP BY id_municipio;
# Opção B — SIDRA tabela 5177 (sidrapy) ; Opção C — XLS por UF no FTP do IBGE.
# Saída esperada: internet_2010_municipios.csv  (municipio_id[7], internet_share[0-1])
print("Rode este script fora do sandbox. Ver instruções no cabeçalho (Opção A/B/C).")

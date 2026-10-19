# input/ — Bases originais (NÃO modificar)

| Arquivo | Fonte | Conteúdo |
|---|---|---|
| `tabela2094_ibge.csv` | IBGE, Censo 2010 (SIDRA tab. 2094) | População total e evangélica por município. |
| `ibge_pib_2010_com_id_municipio.csv` | IBGE, PIB dos Municípios 2010 | PIB municipal + código IBGE. |
| `tabela_sinan.csv` **(não versionado, ~692 MB)** | Ministério da Saúde, SINAN (via basedosdados) | Notificações de violência 2009–2019. |
| `Meu_Municipio_Cobertura.csv` **(não versionado, ~130 MB)** | ANATEL, "Meu Município" | Cobertura de banda larga 2021–2025 (não usada: não sobrepõe o SINAN). |

**Por que dois arquivos não estão aqui:** excedem o limite de tamanho do GitHub. O agregado do SINAN já
processado acompanha o pacote em `tmp/sinan_mun_ano.csv` (basta rodar `01`/`02`). Para regenerar do zero:
baixe `tabela_sinan.csv` (SINAN via basedosdados) para esta pasta e rode `python code/_master.py`
(o passo `00_agrega_sinan.py` fará a agregação em chunks).

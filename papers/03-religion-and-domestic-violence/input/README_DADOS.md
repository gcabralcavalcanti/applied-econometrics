# input/ — source data

| File | Source | Content |
|---|---|---|
| `tabela2094_ibge.csv` | IBGE, Census 2010, SIDRA table 2094, downloaded by `code/00_download_ibge.py` | Total and evangelical population by municipality |
| `ibge_pib_2010_com_id_municipio.csv` | IBGE, municipal GDP 2010, SIDRA table 5938, downloaded by `code/00_download_ibge.py` | GDP and IBGE code |
| `tabela_sinan.csv` **(not versioned, ~692 MB)** | Ministry of Health, SINAN violence microdata (public, via basedosdados) | Notifications 2009–2019 |

The SINAN extract exceeds GitHub's size limit. Its municipality-year aggregate, produced by `code/00_aggregate_sinan.py`,
ships in `tmp/sinan_mun_ano.csv`. To rebuild it, place `tabela_sinan.csv` here and run `python run_all.py 03` from the repository root.

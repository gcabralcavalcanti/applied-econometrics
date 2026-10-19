# -*- coding: utf-8 -*-
# =========================================================================
# 00_agrega_sinan.py — Q4 (Grupo 02) — Econometria I 2026.1
# Objetivo : agrega o SINAN bruto (input/tabela_sinan.csv, ~692MB) em contagens
#            município x ano de violência doméstica feminina.
# Autor    : Grupo 02 (código com auxílio de IA; ver prompts.md)
# Modif.   : 2026-07-01
# Inputs   : input/tabela_sinan.csv  (bruto; NÃO versionado por tamanho)
# Outputs  : tmp/sinan_mun_ano.csv   (municipio_id;ano;n_total;n_dom;n_dom_s0)
# Obs.     : violência doméstica = agressor íntimo/familiar (cônjuge/ex, namorado/ex,
#            pais, padrasto/madrasta, filho, irmão). sexo_paciente: 0=feminino.
#            Se o bruto não estiver em input/, este passo é pulado (use tmp/ incluído).
# =========================================================================
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent.parent; RAW=ROOT/"input"/"tabela_sinan.csv"; OUT=ROOT/"tmp"/"sinan_mun_ano.csv"
if not RAW.exists():
    print(f"[00] {RAW.name} ausente — passo pulado (usando {OUT.name} já incluído em tmp/)."); raise SystemExit(0)
AUT=['autor_pai','autor_mae','autor_padrasto','autor_madrasta','autor_conjugue','autor_ex_conjugue',
     'autor_namorado_a','autor_ex_namorado_a','autor_filho_a','autor_irmao']
cols=['ano','id_municipio_ocorrencia','sexo_paciente']+AUT
agg={}
for ch in pd.read_csv(RAW,sep=';',usecols=cols,dtype=str,chunksize=300000):
    dom=(ch[AUT]=='1').any(axis=1)
    ch=ch.assign(dom=dom, fem=(ch['sexo_paciente']=='0'))
    ch=ch[ch['id_municipio_ocorrencia'].str.match(r'^\d{7}$',na=False) & ch['ano'].str.match(r'^\d{4}$',na=False)]
    for (mun,ano),g in ch.groupby(['id_municipio_ocorrencia','ano']):
        k=(mun,ano); a=agg.get(k,[0,0,0]); a[0]+=len(g); a[1]+=int(g['dom'].sum()); a[2]+=int((g['dom']&g['fem']).sum()); agg[k]=a
df=pd.DataFrame([(m,a,*v) for (m,a),v in agg.items()],columns=['municipio_id','ano','n_total','n_dom','n_dom_s0'])
df.to_csv(OUT,sep=';',index=False); print(f"[00] {len(df)} linhas -> {OUT}")

# -*- coding: utf-8 -*-
# =========================================================================
# 01_monta_base.py — Q4 (Grupo 02) — Econometria I 2026.1
# Objetivo : monta a base municipal de corte transversal (controles + cortes).
# Autor    : Grupo 02 (código com auxílio de IA; ver prompts.md)
# Modif.   : 2026-07-01
# Inputs   : tmp/sinan_mun_ano.csv ; input/tabela2094_ibge.csv ; input/ibge_pib_2010_com_id_municipio.csv
# Outputs  : tmp/controles.csv ; tmp/base_corte_2011_2013.csv ; tmp/base_corte_2013_2015.csv
# Notas    : remove renda pc < R$500 (erros) e winsoriza renda (1/99). Denominador = pop total
#            (limitação: ideal seriam mulheres em risco; ver artigo).
# =========================================================================
from pathlib import Path
import pandas as pd, numpy as np, unicodedata, re
ROOT=Path(__file__).resolve().parent.parent; INP=ROOT/"input"; TMP=ROOT/"tmp"
UFm={11:'RO',12:'AC',13:'AM',14:'RR',15:'PA',16:'AP',17:'TO',21:'MA',22:'PI',23:'CE',24:'RN',25:'PB',26:'PE',
     27:'AL',28:'SE',29:'BA',31:'MG',32:'ES',33:'RJ',35:'SP',41:'PR',42:'SC',43:'RS',50:'MS',51:'MT',52:'GO',53:'DF'}
def norm(s):
    if pd.isna(s): return ''
    s=str(s).strip().upper().strip('"'); s=''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c))
    s=s.replace("'","").replace("`","").replace("-"," "); return re.sub(r'\s+',' ',re.sub(r'[^A-Z0-9 ]','',s)).strip()
def winsor(s,lo=.01,hi=.99): a,b=s.quantile([lo,hi]); return s.clip(a,b)
# controles: IBGE 2094 (pop + evangélicos) + PIB
ib=pd.read_csv(INP/"tabela2094_ibge.csv",sep=';',skiprows=5,header=None,names=['municipio','religiao','valor'],dtype=str,encoding='utf-8',on_bad_lines='skip')
ib['religiao']=ib['religiao'].astype(str).str.strip().str.strip('"')
ib=ib[ib['religiao'].str.fullmatch('Total',case=False)|ib['religiao'].str.contains('vang',case=False,na=False)].copy()
ib['relcat']=np.where(ib['religiao'].str.contains('vang',case=False,na=False),'evang','total')
def pv(x):
    x=str(x).strip().strip('"').replace('.','').replace(',','.')
    try:return float(x)
    except:return np.nan
ib['valor']=ib['valor'].map(pv); ib['uf']=ib['municipio'].str.extract(r'\(([A-Za-z]{2})\)\s*$')[0].str.upper()
ib['nome_norm']=ib['municipio'].str.replace(r'\s*\([A-Za-z]{2}\)\s*$','',regex=True).map(norm)
pv2=ib.pivot_table(index=['nome_norm','uf'],columns='relcat',values='valor',aggfunc='first').reset_index().rename(columns={'total':'pop_total','evang':'pop_evang'})
pv2=pv2[pv2['pop_total']>0].copy(); pv2['pop_evang']=pv2['pop_evang'].fillna(0); pv2['evangelical_density']=pv2['pop_evang']/pv2['pop_total']*100
pib=pd.read_csv(INP/"ibge_pib_2010_com_id_municipio.csv",sep=';',dtype=str)
pib=pib.rename(columns={pib.columns[0]:'id_municipio',pib.columns[1]:'pib',pib.columns[2]:'nome'})[['id_municipio','pib','nome']]
pib['id_municipio']=pib['id_municipio'].str.extract(r'(\d+)')[0].str.zfill(7); pib['pib']=pd.to_numeric(pib['pib'].str.replace(r'[^0-9]','',regex=True),errors='coerce')
pib=pib.dropna(subset=['id_municipio']); pib['uf']=pib['id_municipio'].str[:2].astype(int).map(UFm); pib['nome_norm']=pib['nome'].map(norm)
cw=pv2.merge(pib[['id_municipio','nome_norm','uf','pib']],on=['nome_norm','uf'],how='left').dropna(subset=['id_municipio'])
cw['municipio_id']=cw['id_municipio'].str.zfill(7)
ctl=cw[['municipio_id','pop_total','evangelical_density','pib']].drop_duplicates('municipio_id').copy()
ctl['renda_percapita']=ctl['pib']/ctl['pop_total']
ctl=ctl[ctl['renda_percapita']>=500].copy(); ctl['renda_percapita']=winsor(ctl['renda_percapita']); ctl['uf']=ctl['municipio_id'].str[:2]
ctl.to_csv(TMP/"controles.csv",index=False)
# cortes transversais
sin=pd.read_csv(TMP/"sinan_mun_ano.csv",sep=';',dtype={'municipio_id':str}); sin['municipio_id']=sin['municipio_id'].str.zfill(7)
def xsec(a,b):
    s=sin[(sin.ano>=a)&(sin.ano<=b)].groupby('municipio_id').agg(vd_fem=('n_dom_s0','sum'),n_dom=('n_dom','sum'),n_total=('n_total','sum'),anos=('ano','nunique')).reset_index()
    g=s.merge(ctl,on='municipio_id',how='inner')
    g['vd']=g['vd_fem']/g['anos']/g['pop_total']*1000; g['notif_nondom']=(g['n_total']-g['n_dom'])/g['anos']/g['pop_total']*1000
    g['l_renda']=np.log(g['renda_percapita']); g['l_pop']=np.log(g['pop_total']); g['evang']=g['evangelical_density']
    g['evang2c']=g['evang']**2/100; g['lvd']=np.log1p(g['vd']); g['vd_count']=g['vd_fem']; return g
xsec(2011,2013).to_csv(TMP/"base_corte_2011_2013.csv",index=False)
xsec(2013,2015).to_csv(TMP/"base_corte_2013_2015.csv",index=False)
print(f"[01] controles={len(ctl)} | base 2011-13 salva.")

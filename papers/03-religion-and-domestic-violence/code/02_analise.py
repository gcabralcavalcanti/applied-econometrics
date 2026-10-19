# -*- coding: utf-8 -*-
# =========================================================================
# 02_analise.py — Q4 (Grupo 02) — Econometria I 2026.1
# Objetivo : estima os modelos (MQO/HC1, quadrático, log, proxy de reporte, WLS,
#            Poisson), roda robustez e gera tabelas (.tex) e figuras.
# Autor    : Grupo 02 (código com auxílio de IA; ver prompts.md)
# Modif.   : 2026-07-01
# Inputs   : tmp/base_corte_2011_2013.csv ; tmp/base_corte_2013_2015.csv ; tmp/controles.csv ; tmp/sinan_mun_ano.csv
# Outputs  : output/tables/*.tex ; output/tables/_stats.txt ; output/figures/*.pdf|png
# =========================================================================
from pathlib import Path
import pandas as pd, numpy as np
import statsmodels.api as sm, statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_white
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent.parent; TMP=ROOT/"tmp"; TAB=ROOT/"output"/"tables"; FIG=ROOT/"output"/"figures"
TAB.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
xs=pd.read_csv(TMP/"base_corte_2011_2013.csv",dtype={'municipio_id':str}); xs['uf']=xs['municipio_id'].str.zfill(7).str[:2]
xs2=pd.read_csv(TMP/"base_corte_2013_2015.csv",dtype={'municipio_id':str}); xs2['uf']=xs2['municipio_id'].str.zfill(7).str[:2]
ctl=pd.read_csv(TMP/"controles.csv",dtype={'municipio_id':str}); ctl['municipio_id']=ctl['municipio_id'].str.zfill(7)
sin=pd.read_csv(TMP/"sinan_mun_ano.csv",sep=';',dtype={'municipio_id':str}); sin['municipio_id']=sin['municipio_id'].str.zfill(7)
common=set(xs.municipio_id)&set(xs2.municipio_id); xsc=xs[xs.municipio_id.isin(common)]; xs2c=xs2[xs2.municipio_id.isin(common)]
CAPS={'1200401','2704302','1600303','1302603','2927408','2304400','5300108','3205309','5208707','2111300','5103403','5002704','3106200','1501402','2507507','4106902','2611606','2211001','3304557','2408102','4314902','1100205','1400100','4205407','3550308','2800308','1721000'}
def star(p): return '***' if p<.01 else '**' if p<.05 else '*' if p<.10 else ''
def cell(m,t): return (f"{m.params[t]:.4f}{star(m.pvalues[t])}",f"({m.bse[t]:.4f})") if t in m.params.index else ("","")
def ols(d,f,w=None,cl=None):
    kw=dict(cov_type='cluster',cov_kwds={'groups':d[cl]}) if cl else dict(cov_type='HC1')
    return smf.wls(f,d,weights=d[w]).fit(**kw) if w else smf.ols(f,d).fit(**kw)
F="vd ~ evang + l_renda + l_pop + C(uf)"
m1=ols(xs,F); m2=ols(xs,"vd ~ evang + evang2c + l_renda + l_pop + C(uf)"); m3=ols(xs,"lvd ~ evang + l_renda + l_pop + C(uf)")
m4=ols(xs,"vd ~ evang + l_renda + l_pop + notif_nondom + C(uf)"); m5=ols(xs,F,w='pop_total')
poi=smf.glm("vd_count ~ evang + l_renda + l_pop + C(uf)",xs,family=sm.families.Poisson(),offset=np.log(xs['pop_total'])).fit(cov_type='HC1')
lm,lmp,_,_=het_white(m1.resid,m1.model.exog); k=int(m1.df_model); zeros=(xs['vd']==0).mean()*100
sh=sin[(sin.ano>=2011)&(sin.ano<=2013)]; share=sh['n_dom_s0'].sum()/sh['n_total'].sum()*100
labs=[('vd','Taxa de VD doméstica feminina (por mil hab.)'),('evang','Densidade evangélica (\\%)'),('renda_percapita','Renda per capita (R\\$)'),('pop_total','População'),('notif_nondom','Notificações não-domésticas (por mil)')]
open(TAB/"tab_descritivas.tex","w",encoding="utf-8").write("\\begin{tabular}{lrrrrrr}\n\\toprule\nVariável & N & Média & DP & Mín & Mediana & Máx \\\\\n\\midrule\n"+"".join(f"{l} & {int(xs[v].count())} & {xs[v].mean():,.2f} & {xs[v].std():,.2f} & {xs[v].min():,.2f} & {xs[v].median():,.2f} & {xs[v].max():,.2f} \\\\\n" for v,l in labs)+"\\bottomrule\n\\end{tabular}\n")
mods=[('(1)',m1),('(2)',m2),('(3)',m3),('(4)',m4),('(5)',m5)]; terms=[('evang','Densidade evangélica'),('evang2c','Densidade evangélica$^2$/100'),('l_renda','log(Renda pc)'),('l_pop','log(População)'),('notif_nondom','Notif. não-domésticas')]
with open(TAB/"tab_principal.tex","w",encoding="utf-8") as f:
    f.write("\\begin{tabular}{lccccc}\n\\toprule\n& (1) & (2) & (3) & (4) & (5) \\\\\nDependente & VD & VD & log(1+VD) & VD & VD \\\\\nEstimador & MQO & MQO & MQO & MQO & WLS \\\\\n\\midrule\n")
    for t,l in terms:
        a=[cell(m,t) for _,m in mods]; f.write(l+"".join(" & "+x[0] for x in a)+" \\\\\n"+"".join(" & "+x[1] for x in a)+" \\\\\n")
    f.write("\\midrule\nEfeitos fixos de UF"+" & Sim"*5+" \\\\\nObservações"+"".join(f" & {int(m.nobs)}" for _,m in mods)+" \\\\\n$R^2$"+"".join(f" & {m.rsquared:.3f}" for _,m in mods)+" \\\\\n\\bottomrule\n\\end{tabular}\n")
rb=[('Base 2011–13',ols(xs,F)),('2011–13 (comum)',ols(xsc,F)),('2013–15 (comum)',ols(xs2c,F)),('Sem capitais',ols(xs[~xs.municipio_id.isin(CAPS)],F)),('Cluster UF',ols(xs,F,cl='uf')),('Pop. $\\geq$ 5k',ols(xs[xs.pop_total>=5000],F))]
with open(TAB/"tab_robustez.tex","w",encoding="utf-8") as f:
    f.write("\\begin{tabular}{l"+"c"*len(rb)+"}\n\\toprule\n& "+" & ".join(n for n,_ in rb)+" \\\\\n\\midrule\nDensidade evangélica"+"".join(" & "+cell(m,'evang')[0] for _,m in rb)+" \\\\\n"+"".join(" & "+cell(m,'evang')[1] for _,m in rb)+" \\\\\n\\midrule\nControles+EF UF"+" & Sim"*len(rb)+" \\\\\nObservações"+"".join(f" & {int(m.nobs)}" for _,m in rb)+" \\\\\n$R^2$"+"".join(f" & {m.rsquared:.3f}" for _,m in rb)+" \\\\\n\\bottomrule\n\\end{tabular}\n")
with open(TAB/"tab_poisson.tex","w",encoding="utf-8") as f:
    f.write("\\begin{tabular}{lcc}\n\\toprule\n& Coef. & IRR \\\\\n\\midrule\n")
    for t,l in [('evang','Densidade evangélica'),('l_renda','log(Renda pc)')]: f.write(f"{l} & {poi.params[t]:.4f}{star(poi.pvalues[t])} & {np.exp(poi.params[t]):.4f} \\\\\n & ({poi.bse[t]:.4f}) & \\\\\n")
    f.write(f"\\midrule\nOffset log(pop.) & Sim & \\\\\nEF de UF & Sim & \\\\\nObservações & {int(poi.nobs)} & \\\\\n\\bottomrule\n\\end{{tabular}}\n".replace("{{","{").replace("}}","}"))
open(TAB/"_stats.txt","w",encoding="utf-8").write(f"share_vd_total={share:.1f}\nzeros_pct={zeros:.1f}\nWhite_LM={lm:.1f}\nWhite_gl={k}\nWhite_p={lmp:.2g}\nF={m1.fvalue:.1f}\nFgl=({k},{int(m1.df_resid)})\nN_base={int(m1.nobs)}\nR2_M1={m1.rsquared:.3f}\nR2_M4={m4.rsquared:.3f}\nproxy_b={m4.params['notif_nondom']:.4f}\nproxy_p={m4.pvalues['notif_nondom']:.2g}\nevang_M1={m1.params['evang']:.4f}\nevang_M1_p={m1.pvalues['evang']:.3g}\nevang_2013={rb[2][1].params['evang']:.4f}\nevang_2013_p={rb[2][1].pvalues['evang']:.3g}\ncommon={len(common)}\n")
def binsc(x,y,nb=20):
    q=pd.qcut(x,nb,duplicates='drop'); g=pd.DataFrame({'x':x,'y':y,'q':q}).groupby('q',observed=True); return g['x'].mean(),g['y'].mean()
plt.rcParams.update({'font.size':11,'figure.dpi':120})
for xv,xl,fn in [('evang','Densidade evangélica (%)','fig_evang_vd'),('notif_nondom','Notificações não-domésticas (por mil)','fig_proxy_vd')]:
    bx,by=binsc(xs[xv],xs['vd']); fig,ax=plt.subplots(figsize=(5.2,3.6)); ax.scatter(bx,by,color='#3b6ea5',s=28)
    b,a=np.polyfit(xs[xv],xs['vd'],1); xx=np.linspace(xs[xv].min(),xs[xv].max(),50); ax.plot(xx,a+b*xx,color='#c0392b',lw=1.6)
    ax.set_xlabel(xl); ax.set_ylabel('Taxa de VD doméstica (por mil)'); fig.tight_layout(); fig.savefig(FIG/f"{fn}.pdf"); fig.savefig(FIG/f"{fn}.png"); plt.close()
def xw(a,b):
    s=sin[(sin.ano>=a)&(sin.ano<=b)].groupby('municipio_id').agg(vf=('n_dom_s0','sum'),an=('ano','nunique')).reset_index().merge(ctl,on='municipio_id',how='inner')
    s['vd']=s['vf']/s['an']/s['pop_total']*1000; s['l_renda']=np.log(s['renda_percapita']); s['l_pop']=np.log(s['pop_total']); s['evang']=s['evangelical_density']; return s
rows=[(f"{a}-{a+2}",*(lambda m:(m.params['evang'],m.bse['evang']))(ols(xw(a,a+2),F))) for a in range(2009,2018)]
fig,ax=plt.subplots(figsize=(6.4,3.8)); ax.errorbar(range(len(rows)),[r[1] for r in rows],yerr=[1.96*r[2] for r in rows],fmt='o',color='#3b6ea5',capsize=3)
ax.axhline(0,color='#c0392b',lw=1,ls='--'); ax.set_xticks(range(len(rows))); ax.set_xticklabels([r[0] for r in rows],rotation=45,ha='right',fontsize=8)
ax.set_ylabel('Coef. densidade evangélica'); ax.set_title('Coeficiente por janela móvel de 3 anos (IC 95%)'); fig.tight_layout(); fig.savefig(FIG/"fig_coef_janelas.pdf"); fig.savefig(FIG/"fig_coef_janelas.png"); plt.close()
print(f"[02] OK. N={int(m1.nobs)} R2_M1={m1.rsquared:.3f} R2_M4={m4.rsquared:.3f} evang_M1={m1.params['evang']:+.4f}(p={m1.pvalues['evang']:.2g}) zeros={zeros:.1f}% share={share:.1f}%")

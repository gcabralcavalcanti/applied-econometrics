# -*- coding: utf-8 -*-
# =========================================================================
# 03_refino_denominador.py — refinement added after submission (not in the graded tables).
# Objetivo : the data checks found that 43% of municipalities have a year in 2011-2013 with
#            no SINAN record. 01_monta_base divides by the years that EXIST (anos), so a
#            municipality with records in 2 of 3 years gets its rate overstated by 50%.
#            Here the rate is divided by the full 3 years (a missing year = zero cases) and
#            the main model (1) and the proxy model (4) are re-estimated.
# Inputs   : tmp/base_corte_2011_2013.csv
# Outputs  : output/tables/tab_refino_denominador.tex ; output/tables/_refino.txt
# =========================================================================
from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
TMP, TAB = ROOT / "tmp", ROOT / "output" / "tables"
xs = pd.read_csv(TMP / "base_corte_2011_2013.csv", dtype={"municipio_id": str})
xs["uf"] = xs["municipio_id"].str.zfill(7).str[:2]
# same numerator, full 3-year denominator
xs["vd3"] = xs["vd_fem"] / 3 / xs["pop_total"] * 1000
xs["nd3"] = (xs["n_total"] - xs["n_dom"]) / 3 / xs["pop_total"] * 1000


def star(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""


fits = [
    ("(1) as submitted", smf.ols("vd ~ evang + l_renda + l_pop + C(uf)", xs).fit(cov_type="HC1"), "notif_nondom"),
    ("(1) 3-year denominator", smf.ols("vd3 ~ evang + l_renda + l_pop + C(uf)", xs).fit(cov_type="HC1"), "nd3"),
    ("(4) as submitted", smf.ols("vd ~ evang + l_renda + l_pop + notif_nondom + C(uf)", xs).fit(cov_type="HC1"),
     "notif_nondom"),
    ("(4) 3-year denominator", smf.ols("vd3 ~ evang + l_renda + l_pop + nd3 + C(uf)", xs).fit(cov_type="HC1"), "nd3"),
]
with open(TAB / "tab_refino_denominador.tex", "w", encoding="utf-8") as f:
    f.write("\\begin{tabular}{lcccc}\n\\toprule\n& " + " & ".join(n for n, _, _ in fits) + " \\\\\n\\midrule\n")
    f.write("Densidade evangélica" + "".join(f" & {m.params['evang']:.4f}{star(m.pvalues['evang'])}" for _, m, _ in fits)
            + " \\\\\n" + "".join(f" & ({m.bse['evang']:.4f})" for _, m, _ in fits) + " \\\\\n")
    f.write("Notif. não-domésticas" + "".join(
        f" & {m.params[p]:.4f}{star(m.pvalues[p])}" if p in m.params.index else " & " for _, m, p in fits) + " \\\\\n")
    f.write("\\midrule\nObservações" + "".join(f" & {int(m.nobs)}" for _, m, _ in fits)
            + " \\\\\n$R^2$" + "".join(f" & {m.rsquared:.3f}" for _, m, _ in fits) + " \\\\\n\\bottomrule\n\\end{tabular}\n")
partial = int((xs["anos"] < 3).sum())
(TAB / "_refino.txt").write_text(
    f"municipios_ano_sem_registro={partial}\nshare_ano_sem_registro={partial / len(xs) * 100:.1f}\n"
    f"evang_3anos={fits[1][1].params['evang']:.4f}\nevang_3anos_p={fits[1][1].pvalues['evang']:.3g}\n"
    f"R2_3anos={fits[1][1].rsquared:.3f}\nmedia_vd={xs['vd'].mean():.3f}\nmedia_vd3={xs['vd3'].mean():.3f}\n",
    encoding="utf-8")
print("[03] refinement:", " | ".join(f"{n}: {m.params['evang']:+.4f} (p={m.pvalues['evang']:.2g}, R2={m.rsquared:.3f})"
                                     for n, m, _ in fits))

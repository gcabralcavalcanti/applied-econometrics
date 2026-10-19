"""
q4_checks - automatic checks on the municipal base, run after 01_monta_base and before
02_analise. Writes output/data_checks.json.

The fragile step in this paper is the merge: the Census religion table (SIDRA 2094) has
municipality NAMES, the GDP table has IBGE CODES, and SINAN has codes. The checks below
cross the result against the official list of municipalities from the IBGE API.

What could silently go wrong here, and the check that catches it:
 - name matching drops or mismatches municipalities  -> coverage and IBGE API name check
 - SINAN sex coded 0/1 (filtering on 'F' gave zero)  -> female count <= domestic count, > 0
 - a municipality with no notification in a year     -> years-averaged warning (see README)
"""
import gzip
import json
import sys
import unicodedata
import urllib.request
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
REPO = RAIZ.parent.parent
sys.path.insert(0, str(REPO))
from aecon.checks import Report, WARN  # noqa: E402

TMP, INP = RAIZ / "tmp", RAIZ / "input"
IBGE_API = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
CACHE = REPO / ".cache" / "ibge_municipios.json"


def ibge_municipalities() -> pd.DataFrame | None:
    """Official list of municipalities (code, name) from the IBGE API; cached after the first download."""
    if not CACHE.exists():
        try:
            with urllib.request.urlopen(IBGE_API, timeout=30) as resp:
                raw = resp.read()
            data = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)  # the API gzips
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps([{"id": d["id"], "nome": d["nome"]} for d in data],
                                        ensure_ascii=False), encoding="utf-8")
        except OSError:
            return None
    return pd.DataFrame(json.loads(CACHE.read_text(encoding="utf-8")))


def norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s).upper()) if not unicodedata.combining(c))
    return "".join(c for c in s if c.isalnum())


sin = pd.read_csv(TMP / "sinan_mun_ano.csv", sep=";", dtype={"municipio_id": str})
ctl = pd.read_csv(TMP / "controles.csv", dtype={"municipio_id": str})
xs = pd.read_csv(TMP / "base_corte_2011_2013.csv", dtype={"municipio_id": str})
pib = pd.read_csv(INP / "ibge_pib_2010_com_id_municipio.csv", sep=";", dtype=str)

r = Report("03-religion-and-domestic-violence",
           [TMP / "sinan_mun_ano.csv", INP / "tabela2094_ibge.csv", INP / "ibge_pib_2010_com_id_municipio.csv",
            TMP / "base_corte_2011_2013.csv"])

# SINAN aggregate
r.in_range(sin["ano"], 2009, 2019, "SINAN year", "")
r.no_duplicates(sin, ["municipio_id", "ano"])
r.add("SINAN counts are consistent: female <= domestic <= total",
      bool(((sin["n_dom_s0"] <= sin["n_dom"]) & (sin["n_dom"] <= sin["n_total"])).all()),
      "holds in every municipality-year", None)
r.add("SINAN sex coding produces female victims (0/1 coding, not 'F')", sin["n_dom_s0"].sum() > 0,
      f"{int(sin['n_dom_s0'].sum()):,} female domestic-violence notifications", int(sin["n_dom_s0"].sum()))
r.add("municipality codes have 7 digits", sin["municipio_id"].str.fullmatch(r"\d{7}").all()
      and ctl["municipio_id"].str.zfill(7).str.fullmatch(r"\d{7}").all(), "SINAN and controls", None)

# merge coverage (names in SIDRA 2094 -> codes in the GDP table)
n_pib = int(pib.iloc[:, 0].str.extract(r"(\d{7})")[0].notna().sum())
cov = len(ctl) / n_pib
r.add("merge coverage: controls / municipalities in the GDP table", cov > 0.95,
      f"{len(ctl)} of {n_pib} ({cov:.1%}); the rest failed the name match or the income filter", cov, WARN)
CAPITALS = {"1200401", "2704302", "1600303", "1302603", "2927408", "2304400", "5300108", "3205309", "5208707",
            "2111300", "5103403", "5002704", "3106200", "1501402", "2507507", "4106902", "2611606", "2211001",
            "3304557", "2408102", "4314902", "1100205", "1400100", "4205407", "3550308", "2800308", "1721000"}
lost = sorted(CAPITALS - set(xs["municipio_id"].str.zfill(7)))
r.add("all 27 state capitals are in the base", not lost,
      "all present" if not lost else f"missing capitals {lost}: a failed name match drops the largest cities",
      len(lost))
r.in_range(ctl["evangelical_density"], 0, 100, "evangelical density", "% of residents")
r.in_range(ctl["renda_percapita"], 500, 200_000, "GDP per capita (after filter and winsorising)", "R$")

# official list from the IBGE API
ibge = ibge_municipalities()
if ibge is None:
    r.add("IBGE API: codes and names", False, "API unreachable and no cache; check skipped", None, WARN)
else:
    ibge["municipio_id"] = ibge["id"].astype(str)
    unknown = sorted(set(xs["municipio_id"].str.zfill(7)) - set(ibge["municipio_id"]))
    r.add("IBGE API: every code in the base is an official municipality", not unknown,
          f"{len(xs)} codes checked against {len(ibge)} official municipalities"
          if not unknown else f"unknown codes: {unknown[:10]}", len(unknown))
    pnames = pib.rename(columns={pib.columns[0]: "id", pib.columns[2]: "nome"})
    pnames["municipio_id"] = pnames["id"].str.extract(r"(\d{7})")[0]
    m = pnames.merge(ibge, on="municipio_id", suffixes=("_pib", "_ibge"))
    m = m[m["municipio_id"].isin(xs["municipio_id"].str.zfill(7))]
    diff = m[m["nome_pib"].map(norm) != m["nome_ibge"].map(norm)]
    r.add("IBGE API: names in the GDP table match the official names", len(diff) <= 10,
          f"{len(diff)} of {len(m)} differ (renamed since 2010 or spelling): "
          + ", ".join(f"{a} / {b}" for a, b in diff[["nome_pib", "nome_ibge"]].head(5).values),
          len(diff), WARN)

# the estimation base
r.no_missing(xs, ["vd", "evang", "l_renda", "l_pop", "notif_nondom"], "missing values: regression base")
r.no_duplicates(xs, ["municipio_id"])
partial = int((xs["anos"] < 3).sum())
r.add("every municipality has notifications in all 3 years (2011-2013)", partial == 0,
      f"{partial} municipalities ({partial / len(xs):.1%}) have a year with no record; their rate is "
      "averaged over the years that exist, which overstates it", partial, WARN)
zeros = float((xs["vd"] == 0).mean())
r.add("share of municipalities with zero recorded cases", zeros < 0.25, f"{zeros:.1%} (motivates the Poisson model)",
      zeros, WARN)

r.finish(RAIZ / "output" / "data_checks.json")

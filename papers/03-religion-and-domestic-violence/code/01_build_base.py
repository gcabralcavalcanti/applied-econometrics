"""Build the municipal cross-section: controls plus the 2011-2013 and 2013-2015 windows.

Input:  tmp/sinan_mun_ano.csv, input/tabela2094_ibge.csv, input/ibge_pib_2010_com_id_municipio.csv
Output: tmp/controles.csv, tmp/base_corte_2011_2013.csv, tmp/base_corte_2013_2015.csv

Per capita income below R$500 is treated as a data error and dropped; income is winsorised at 1/99.
The denominator is the whole population (women at risk would be better; see the README).
"""

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"
TMP = ROOT / "tmp"

UF_BY_CODE = {
    11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO",
    21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA",
    31: "MG", 32: "ES", 33: "RJ", 35: "SP",
    41: "PR", 42: "SC", 43: "RS",
    50: "MS", 51: "MT", 52: "GO", 53: "DF",
}  # fmt: skip


def normalize_name(s):
    """Municipality name as a matching key: upper case, no accents or punctuation, single spaces."""
    if pd.isna(s):
        return ""
    s = str(s).strip().upper().strip('"')
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = s.replace("'", "").replace("`", "").replace("-", " ")
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", "", s)).strip()


def winsorize(s, lo=0.01, hi=0.99):
    low, high = s.quantile([lo, hi])
    return s.clip(low, high)


def parse_br_number(x):
    """'1.234,5' -> 1234.5; anything unparseable -> NaN."""
    x = str(x).strip().strip('"').replace(".", "").replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return np.nan


# Controls: Census table 2094 (population and evangelicals) + GDP.
# The census table has municipality names only, so it is matched to the GDP table's codes by name and state.
census = pd.read_csv(
    INPUT_DIR / "tabela2094_ibge.csv",
    sep=";",
    skiprows=5,
    header=None,
    names=["municipio", "religiao", "valor"],
    dtype=str,
    encoding="utf-8",
    on_bad_lines="skip",
)
census["religiao"] = census["religiao"].astype(str).str.strip().str.strip('"')
is_total = census["religiao"].str.fullmatch("Total", case=False)
is_evangelical = census["religiao"].str.contains("vang", case=False, na=False)
census = census[is_total | is_evangelical].copy()
census["relcat"] = np.where(census["religiao"].str.contains("vang", case=False, na=False), "evang", "total")
census["valor"] = census["valor"].map(parse_br_number)
census["uf"] = census["municipio"].str.extract(r"\(([A-Za-z]{2})\)\s*$")[0].str.upper()
census["nome_norm"] = census["municipio"].str.replace(r"\s*\([A-Za-z]{2}\)\s*$", "", regex=True).map(normalize_name)

population = (
    census.pivot_table(index=["nome_norm", "uf"], columns="relcat", values="valor", aggfunc="first")
    .reset_index()
    .rename(columns={"total": "pop_total", "evang": "pop_evang"})
)
population = population[population["pop_total"] > 0].copy()
population["pop_evang"] = population["pop_evang"].fillna(0)
population["evangelical_density"] = population["pop_evang"] / population["pop_total"] * 100

gdp = pd.read_csv(INPUT_DIR / "ibge_pib_2010_com_id_municipio.csv", sep=";", dtype=str)
gdp = gdp.rename(columns={gdp.columns[0]: "id_municipio", gdp.columns[1]: "pib", gdp.columns[2]: "nome"})
gdp = gdp[["id_municipio", "pib", "nome"]]
gdp["id_municipio"] = gdp["id_municipio"].str.extract(r"(\d+)")[0].str.zfill(7)
gdp["pib"] = pd.to_numeric(gdp["pib"].str.replace(r"[^0-9]", "", regex=True), errors="coerce")
gdp = gdp.dropna(subset=["id_municipio"])
gdp["uf"] = gdp["id_municipio"].str[:2].astype(int).map(UF_BY_CODE)
gdp["nome_norm"] = gdp["nome"].map(normalize_name)

crosswalk = population.merge(
    gdp[["id_municipio", "nome_norm", "uf", "pib"]], on=["nome_norm", "uf"], how="left"
).dropna(subset=["id_municipio"])
crosswalk["municipio_id"] = crosswalk["id_municipio"].str.zfill(7)

controls = crosswalk[["municipio_id", "pop_total", "evangelical_density", "pib"]].drop_duplicates("municipio_id").copy()
controls["renda_percapita"] = controls["pib"] / controls["pop_total"]
controls = controls[controls["renda_percapita"] >= 500].copy()
controls["renda_percapita"] = winsorize(controls["renda_percapita"])
controls["uf"] = controls["municipio_id"].str[:2]
controls.to_csv(TMP / "controles.csv", index=False)

# Cross-sections
sinan = pd.read_csv(TMP / "sinan_mun_ano.csv", sep=";", dtype={"municipio_id": str})
sinan["municipio_id"] = sinan["municipio_id"].str.zfill(7)


def cross_section(first_year, last_year):
    """Average yearly rates per 1,000 residents over the window, merged with the controls."""
    window = sinan[(sinan.ano >= first_year) & (sinan.ano <= last_year)]
    summed = (
        window.groupby("municipio_id")
        .agg(
            vd_fem=("n_dom_s0", "sum"),
            n_dom=("n_dom", "sum"),
            n_total=("n_total", "sum"),
            anos=("ano", "nunique"),
        )
        .reset_index()
    )
    base = summed.merge(controls, on="municipio_id", how="inner")
    # divided by the years with records, not the window length (03_refinement_denominator.py tests this)
    base["vd"] = base["vd_fem"] / base["anos"] / base["pop_total"] * 1000
    base["notif_nondom"] = (base["n_total"] - base["n_dom"]) / base["anos"] / base["pop_total"] * 1000
    base["l_renda"] = np.log(base["renda_percapita"])
    base["l_pop"] = np.log(base["pop_total"])
    base["evang"] = base["evangelical_density"]
    base["evang2c"] = base["evang"] ** 2 / 100
    base["lvd"] = np.log1p(base["vd"])
    base["vd_count"] = base["vd_fem"]
    return base


cross_section(2011, 2013).to_csv(TMP / "base_corte_2011_2013.csv", index=False)
cross_section(2013, 2015).to_csv(TMP / "base_corte_2013_2015.csv", index=False)
print(f"[01] controls={len(controls)} | cross-sections 2011-13 and 2013-15 saved.")

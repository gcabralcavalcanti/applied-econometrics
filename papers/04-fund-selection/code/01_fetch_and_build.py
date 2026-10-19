"""
01_fetch_and_build - pulls public CVM fund data and the CDI, and builds the monthly panel.

Sources (all public, no login):
  CVM daily fund reports  dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_YYYYMM.zip  (quota, net assets)
  CVM fund factsheets     dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/lamina_fi_YYYYMM.zip  (fees, expense ratio)
  CVM registers           FI/CAD/DADOS/cad_fi.csv (old regime), registro_fundo_classe.zip (Res. 175) -> asset class
  CDI, monthly %          BCB SGS series 4391

Why the factsheet (lâmina): only funds sold to the general public must publish one, so "has a factsheet in
December of year t" defines the menu a retail investor could pick from at that date, with the fees stated at that
date. Building the menu at each date, not from today's survivors, keeps closed funds in the sample.

The zips (~750 MB) go to .cache/cvm/ (not versioned). Only month-end quotas of menu funds are kept, so the
versioned output in data/ is small and the paper runs offline.

Outputs: data/menu.csv (year, fund, asset class, admin fee, expense ratio, performance fee)
         data/monthly_quotas.csv.gz (fund, month, month-end quota, net assets, investors)
         data/cdi.csv (month, CDI %)
"""

import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
CACHE = REPO / ".cache" / "cvm"
DATA = ROOT / "data"
BASE = "https://dados.cvm.gov.br/dados/FI"
MONTHS = pd.period_range("2021-01", "2026-09", freq="M")  # last complete month at the time of the run
MENU_YEARS = range(2021, 2026)  # December factsheets 2021-2025
CLASSES = {"Ações": "Equity", "Multimercado": "Multi-asset", "Renda Fixa": "Fixed income"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        print(f"  downloading {url}")
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, path)
    return path


def fmt_cnpj(s: str) -> str:
    s = str(s).zfill(14)
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}"


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False).str.strip(), errors="coerce")


def asset_class() -> pd.Series:
    """CNPJ -> asset class, from both registers (the new one wins)."""
    cad = pd.read_csv(
        download(f"{BASE}/CAD/DADOS/cad_fi.csv", CACHE / "cad_fi.csv"),
        sep=";",
        encoding="latin1",
        usecols=["CNPJ_FUNDO", "CLASSE"],
        dtype=str,
    )
    old = cad.dropna().drop_duplicates("CNPJ_FUNDO").set_index("CNPJ_FUNDO")["CLASSE"]
    z = zipfile.ZipFile(download(f"{BASE}/CAD/DADOS/registro_fundo_classe.zip", CACHE / "registro_fundo_classe.zip"))
    reg = pd.read_csv(
        z.open("registro_classe.csv"), sep=";", encoding="latin1", dtype=str, usecols=["CNPJ_Classe", "Classificacao"]
    ).dropna()
    new = reg.assign(cnpj=reg["CNPJ_Classe"].map(fmt_cnpj)).drop_duplicates("cnpj").set_index("cnpj")["Classificacao"]
    both = pd.concat([old[~old.index.isin(new.index)], new])
    return both.map(CLASSES)


def menu() -> pd.DataFrame:
    classes = asset_class()
    rows, skipped = [], {}
    for y in MENU_YEARS:
        ym = f"{y}12"
        z = zipfile.ZipFile(download(f"{BASE}/DOC/LAMINA/DADOS/lamina_fi_{ym}.zip", CACHE / f"lamina_fi_{ym}.zip"))
        bad = []  # free-text fields sometimes carry stray separators; those rows are counted and dropped
        lam = pd.read_csv(
            z.open(f"lamina_fi_{ym}.csv"),
            sep=";",
            encoding="latin1",
            dtype=str,
            engine="python",
            on_bad_lines=lambda line, bad=bad: bad.append(line[:2]) and None,
        )
        skipped[ym] = len(bad)
        lam = lam.rename(columns={"CNPJ_FUNDO_CLASSE": "CNPJ_FUNDO"})
        if "ID_SUBCLASSE" in lam:  # one row per class: the class row, or its first subclass if it only has those
            lam = lam.sort_values("ID_SUBCLASSE", na_position="first")
        lam = lam.sort_values("DT_COMPTC").drop_duplicates("CNPJ_FUNDO", keep="last")
        rows.append(
            pd.DataFrame(
                {
                    "year": y,
                    "fund": lam["CNPJ_FUNDO"].values,
                    "asset_class": lam["CNPJ_FUNDO"].map(classes).values,
                    "admin_fee": to_num(lam["TAXA_ADM"]).values,
                    "expense_ratio": to_num(lam["PR_PL_DESPESA"]).values,
                    "perf_fee": to_num(lam["TAXA_PERFM"]).fillna(0).gt(0).values,
                }
            )
        )
        print(f"  factsheets {ym}: {len(lam)} funds, {len(bad)} malformed rows skipped")
    m = pd.concat(rows, ignore_index=True)
    pd.Series(skipped, name="malformed_rows").rename_axis("factsheet").to_csv(DATA / "factsheet_skipped_rows.csv")
    return m[m["asset_class"].notna()]


def month_end_quotas(funds: set) -> pd.DataFrame:
    frames = []
    for p in MONTHS:
        ym = p.strftime("%Y%m")
        d = pd.read_csv(
            download(f"{BASE}/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ym}.zip", CACHE / f"inf_diario_fi_{ym}.zip"),
            sep=";",
            dtype=str,
        )
        # CVM Resolution 175 renamed the columns in late 2024 (fund -> fund class); same CNPJ, same quota series
        d = d.rename(columns={"CNPJ_FUNDO_CLASSE": "CNPJ_FUNDO"})
        if "ID_SUBCLASSE" in d:
            d = d[d["ID_SUBCLASSE"].isna()]
        d = d[d["CNPJ_FUNDO"].isin(funds)]
        d = d.sort_values("DT_COMPTC").groupby("CNPJ_FUNDO").tail(1)
        frames.append(
            pd.DataFrame(
                {
                    "fund": d["CNPJ_FUNDO"],
                    "month": str(p),
                    "date": d["DT_COMPTC"],
                    "quota": d["VL_QUOTA"].astype(float),
                    "net_assets": d["VL_PATRIM_LIQ"].astype(float),
                    "investors": pd.to_numeric(d["NR_COTST"], errors="coerce"),
                }
            )
        )
        print(f"  quotas {p}: {len(d)} funds")
    return pd.concat(frames, ignore_index=True)


def cdi() -> pd.DataFrame:
    from bcb import sgs

    s = sgs.get({"cdi": 4391}, start="2021-01-01")
    s.index = s.index.to_period("M").astype(str)
    return s.loc[[str(p) for p in MONTHS if str(p) in s.index]].rename_axis("month").reset_index()


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    mn = menu()
    mn.to_csv(DATA / "menu.csv", index=False)
    print(f"Menu: {len(mn)} fund-years, {mn['fund'].nunique()} funds")
    qt = month_end_quotas(set(mn["fund"])).drop(columns="date")
    qt["net_assets"] = qt["net_assets"].round(0)
    qt.to_csv(DATA / "monthly_quotas.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    cdi().to_csv(DATA / "cdi.csv", index=False)
    print("Saved data/menu.csv, data/monthly_quotas.csv.gz, data/cdi.csv")

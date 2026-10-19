"""Aggregate the raw SINAN extract into female domestic-violence counts per municipality-year.

Input:  input/tabela_sinan.csv (raw, ~692 MB, not versioned)
Output: tmp/sinan_mun_ano.csv (municipio_id;ano;n_total;n_dom;n_dom_s0)

Domestic violence = the aggressor is an intimate partner or family member (spouse or ex,
partner or ex, parent, step-parent, child, sibling). SINAN codes sex_paciente as 0 = female.
If the raw file is absent the step is skipped and the shipped aggregate in tmp/ is used.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "input" / "tabela_sinan.csv"
OUT = ROOT / "tmp" / "sinan_mun_ano.csv"

AGGRESSOR_COLUMNS = [
    "autor_pai",
    "autor_mae",
    "autor_padrasto",
    "autor_madrasta",
    "autor_conjugue",
    "autor_ex_conjugue",
    "autor_namorado_a",
    "autor_ex_namorado_a",
    "autor_filho_a",
    "autor_irmao",
]


def main() -> None:
    if not RAW.exists():
        print(f"[00] {RAW.name} not found; step skipped (using the {OUT.name} shipped in tmp/).")
        return

    columns = ["ano", "id_municipio_ocorrencia", "sexo_paciente"] + AGGRESSOR_COLUMNS
    counts = {}  # (municipality, year) -> [total, domestic, domestic female]
    for chunk in pd.read_csv(RAW, sep=";", usecols=columns, dtype=str, chunksize=300000):
        domestic = (chunk[AGGRESSOR_COLUMNS] == "1").any(axis=1)
        chunk = chunk.assign(dom=domestic, fem=(chunk["sexo_paciente"] == "0"))
        valid = chunk["id_municipio_ocorrencia"].str.match(r"^\d{7}$", na=False) & chunk["ano"].str.match(
            r"^\d{4}$", na=False
        )
        chunk = chunk[valid]
        for (municipality, year), group in chunk.groupby(["id_municipio_ocorrencia", "ano"]):
            key = (municipality, year)
            totals = counts.get(key, [0, 0, 0])
            totals[0] += len(group)
            totals[1] += int(group["dom"].sum())
            totals[2] += int((group["dom"] & group["fem"]).sum())
            counts[key] = totals

    df = pd.DataFrame(
        [(municipality, year, *totals) for (municipality, year), totals in counts.items()],
        columns=["municipio_id", "ano", "n_total", "n_dom", "n_dom_s0"],
    )
    df.to_csv(OUT, sep=";", index=False)
    print(f"[00] {len(df)} rows -> {OUT}")


if __name__ == "__main__":
    main()

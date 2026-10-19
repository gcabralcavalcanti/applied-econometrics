"""Download the two IBGE inputs from the SIDRA API.

Input:  none (public IBGE SIDRA API)
  table 2094 (Census 2010): resident population, total and evangelicals, by municipality
  table 5938: municipal GDP at current prices, 2010 (thousand R$)
Output: input/tabela2094_ibge.csv, input/ibge_pib_2010_com_id_municipio.csv
        (the layout 01_build_base.py reads: SIDRA CSV with a 5-line header; id;pib;nome)

The evangelical count is a Census sample estimate, so it has decimals (4 kept, as SIDRA shows).
"""

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"
API = "https://apisidra.ibge.gov.br/values"


def sidra(path: str) -> list[dict]:
    with urllib.request.urlopen(f"{API}/{path}", timeout=120) as response:
        rows = json.load(response)
    return rows[1:]  # the first row is the header


def split_name_uf(label: str) -> tuple[str, str]:
    """'Ariquemes - RO' or 'Ariquemes (RO)' -> ('Ariquemes', 'RO')."""
    if label.endswith(")"):
        name, uf = label.rsplit(" (", 1)
        return name, uf.rstrip(")")
    name, uf = label.rsplit(" - ", 1)
    return name, uf


def main() -> None:
    INPUT_DIR.mkdir(exist_ok=True)

    # Total (0) and Evangelicals (95277), all colours/races (0), 4 decimals
    religion = sidra("t/2094/n6/all/v/93/p/2010/c86/0/c133/0,95277/d/v93%204")
    lines = [
        '"Tabela 2094 - População residente por cor ou raça e religião"',
        '"Variável - População residente (Pessoas)"',
        '"Município";"Religião";"Ano x Cor ou raça"',
        '"Município";"Religião";"2010"',
        '"Município";"Religião";"Total"',
    ]
    for row in sorted(religion, key=lambda row: (row["D1C"], row["D5C"])):
        value = row["V"] if row["V"] not in ("-", "...", "X") else "0"
        name, uf = split_name_uf(row["D1N"])
        lines.append(f'"{name} ({uf})";"{row["D5N"]}";"{value.replace(".", ",")}"')
    (INPUT_DIR / "tabela2094_ibge.csv").write_text("﻿" + "\n".join(lines) + "\n", encoding="utf-8")

    # GDP 2010: thousand R$ -> R$
    gdp = sidra("t/5938/n6/all/v/37/p/2010")
    out = ["id_municipio;pib;nome"]
    for row in sorted(gdp, key=lambda row: row["D1C"]):
        if row["V"].isdigit():
            name = split_name_uf(row["D1N"])[0]
            out.append(f"{row['D1C']};{int(row['V']) * 1000};{name}")
    (INPUT_DIR / "ibge_pib_2010_com_id_municipio.csv").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[00] IBGE: {len(religion)} religion rows, {len(out) - 1} municipalities with GDP -> input/")


if __name__ == "__main__":
    main()

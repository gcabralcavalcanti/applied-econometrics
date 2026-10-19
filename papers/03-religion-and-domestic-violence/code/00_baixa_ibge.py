# -*- coding: utf-8 -*-
# =========================================================================
# 00_baixa_ibge.py — downloads the two IBGE inputs from the SIDRA API.
# Inputs   : none (IBGE SIDRA API, public)
#   table 2094 (Census 2010): resident population, total and evangelicals, by municipality
#   table 5938: municipal GDP at current prices, 2010 (thousand R$)
# Outputs  : input/tabela2094_ibge.csv, input/ibge_pib_2010_com_id_municipio.csv
#            (same layout that 01_monta_base reads: SIDRA CSV with a 5-line header; id;pib;nome)
# Notes    : the evangelical count is a Census sample estimate, so it has decimals (4 kept, as SIDRA shows).
# =========================================================================
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INP = ROOT / "input"
API = "https://apisidra.ibge.gov.br/values"


def sidra(path: str) -> list[dict]:
    with urllib.request.urlopen(f"{API}/{path}", timeout=120) as r:
        rows = json.load(r)
    return rows[1:]   # the first row is the header


def name_uf(d1n: str) -> tuple[str, str]:
    """'Ariquemes - RO' or 'Ariquemes (RO)' -> ('Ariquemes', 'RO')."""
    if d1n.endswith(")"):
        n, uf = d1n.rsplit(" (", 1)
        return n, uf.rstrip(")")
    n, uf = d1n.rsplit(" - ", 1)
    return n, uf


def main() -> None:
    INP.mkdir(exist_ok=True)
    # religion: Total (0) and Evangélicas (95277), all colours/races (0), 4 decimals
    rel = sidra("t/2094/n6/all/v/93/p/2010/c86/0/c133/0,95277/d/v93%204")
    lines = ['"Tabela 2094 - População residente por cor ou raça e religião"',
             '"Variável - População residente (Pessoas)"',
             '"Município";"Religião";"Ano x Cor ou raça"',
             '"Município";"Religião";"2010"',
             '"Município";"Religião";"Total"']
    for r in sorted(rel, key=lambda r: (r["D1C"], r["D5C"])):
        v = r["V"] if r["V"] not in ("-", "...", "X") else "0"
        n, uf = name_uf(r["D1N"])
        lines.append(f'"{n} ({uf})";"{r["D5N"]}";"{v.replace(".", ",")}"')
    (INP / "tabela2094_ibge.csv").write_text("﻿" + "\n".join(lines) + "\n", encoding="utf-8")

    # GDP 2010, thousand R$ -> R$
    pib = sidra("t/5938/n6/all/v/37/p/2010")
    out = ["id_municipio;pib;nome"]
    for r in sorted(pib, key=lambda r: r["D1C"]):
        if r["V"].isdigit():
            name = name_uf(r["D1N"])[0]
            out.append(f'{r["D1C"]};{int(r["V"]) * 1000};{name}')
    (INP / "ibge_pib_2010_com_id_municipio.csv").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[00] IBGE: {len(rel)} religion rows, {len(out) - 1} municipalities with GDP -> input/")


if __name__ == "__main__":
    main()

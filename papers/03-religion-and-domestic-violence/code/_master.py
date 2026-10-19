# -*- coding: utf-8 -*-
# =========================================================================
# _master.py — MAESTRO da Questão 4 (Grupo 02) — Econometria I 2026.1
# Objetivo : roda o projeto do início ao fim. Basta editar ROOT (ou deixar automático).
# Ordem    : 00_agrega_sinan (se houver bruto) -> 01_monta_base -> 02_analise
# Saídas   : output/tables/*.tex e output/figures/*
# =========================================================================
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent      # <-- edite aqui se necessário
CODE=ROOT/"code"
for step in ["00_agrega_sinan.py","01_monta_base.py","02_analise.py"]:
    print(f"\n===== {step} =====")
    r=subprocess.run([sys.executable,str(CODE/step)])
    if r.returncode!=0: sys.exit(f"Falhou em {step}")
print("\nConcluído. Tabelas e figuras em output/.")

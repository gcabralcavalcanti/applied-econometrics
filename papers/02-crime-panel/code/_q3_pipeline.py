"""
_q3_pipeline - runner da Questao 3. Roda os scripts q3_1..q3_6 na ordem:
    python code/_q3_pipeline.py

Autor: Guilherme Cabral (Grupo 1)
Data: 27/06/2026
Inputs:  os scripts q3_1..q3_6 em code/
Outputs: a base (tmp/) e os resultados finais (output/: tabelas e figuras).
"""
import runpy
from pathlib import Path

CODDIR = Path(__file__).resolve().parent

PIPELINE_Q3 = [
    "q3_1_carrega_painel.py",
    "q3_2_pooled.py",
    "q3_3_heterocedasticidade.py",
    "q3_4_efeitos_fixos.py",
    "q3_5_duas_vias.py",
    "q3_6_cluster.py",
]

def roda(script):
    print(f"\n{'='*70}\n>>> {script}\n{'='*70}")
    runpy.run_path(str(CODDIR / script), run_name="__main__")

if __name__ == "__main__":
    for script in PIPELINE_Q3:
        roda(script)
    print("\nPipeline da Questao 3 concluido. Resultados finais em output/.")

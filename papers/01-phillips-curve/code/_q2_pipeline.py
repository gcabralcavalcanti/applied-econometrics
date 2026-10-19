"""
_q2_pipeline - runner da Questao 2. Roda os scripts q2_1..q2_7 na ordem, de uma
vez so:
    python code/_q2_pipeline.py
E adicao pura da Q2: NAO mexe no _master.py do grupo. Trocar de maquina nao
exige editar nada (os caminhos saem da posicao deste arquivo).

Autor: Guilherme Cabral (Grupo 1)
Data: 18/06/2026
Inputs:  os scripts q2_1..q2_7 em code/ (q2_1 baixa do BCB; os demais rodam do
         que ja esta em tmp/ e output/)
Outputs: aciona a geracao das series cruas (tmp/) e dos resultados (output/).
"""

import runpy
from pathlib import Path

# caminhos detectados pelo proprio arquivo (igual aos outros scripts)
CODDIR = Path(__file__).resolve().parent
TMPDIR = CODDIR.parent / "tmp"

# ordem de execucao da Q2
PIPELINE_Q2 = [
    "q2_1_baixa_series.py",
    "q2_2_organiza_base.py",
    "q2_3_phillips_estatica.py",
    "q2_4_diagnosticos.py",
    "q2_5_modelo_dinamico.py",
    "q2_6_hac.py",
    "q2_7_robustez.py",
]

def roda(script):
    """Roda um script de code/ como se fosse o __main__ (tipo o source() do R)."""
    print(f"\n{'='*70}\n>>> {script}\n{'='*70}")
    runpy.run_path(str(CODDIR / script), run_name="__main__")

if __name__ == "__main__":
    # o q2_1 precisa de internet (APIs do BCB). se ele falhar mas as series
    # cruas ja estiverem em tmp/, sigo com o cache (q2_2..q2_7 rodam offline).
    series_cache = [TMPDIR / nome for nome in
                    ("q2_ipca.csv", "q2_desemprego.csv", "q2_focus_mensal.csv")]
    for script in PIPELINE_Q2:
        if script == "q2_1_baixa_series.py":
            try:
                roda(script)
            except Exception as erro:
                if all(c.exists() for c in series_cache):
                    print(f"  [aviso] {script} falhou ({type(erro).__name__}); "
                          "uso as series ja salvas em tmp/ e sigo o pipeline.")
                else:
                    raise
        else:
            roda(script)
    print("\nPipeline da Questao 2 concluido. Resultados finais em output/.")

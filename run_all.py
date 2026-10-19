"""
run_all.py - single entry point. For each paper: (download) -> build the base -> data checks
-> estimation -> tables. Then it compares every table with the version submitted for grading.

    python run_all.py                 # all papers, from the shipped data
    python run_all.py --download      # papers 01 and 04 pull their data again first (changes the sample)
    python run_all.py 01 03           # only some papers
    python run_all.py --verify        # only compare the tables on disk with the snapshot
    python run_all.py --review        # also the AI reviewer and the AI committee memo (live with a key,
                                      # recorded answers without)

A data check marked FAIL stops the paper before any regression runs.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAPERS = ROOT / "papers"
SNAPSHOT = ROOT / "tests" / "table_snapshot.json"
# UTF-8 everywhere (Windows consoles default to cp1252; tables contain accents)
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}

STEPS = {
    "01": ("01-phillips-curve", [
        "q2_2_organiza_base.py", "q2_checks.py", "q2_3_phillips_estatica.py", "q2_4_diagnosticos.py",
        "q2_5_modelo_dinamico.py", "q2_6_hac.py", "q2_7_robustez.py"]),
    "02": ("02-crime-panel", [
        "q3_1_carrega_painel.py", "q3_checks.py", "q3_2_pooled.py", "q3_3_heterocedasticidade.py",
        "q3_4_efeitos_fixos.py", "q3_5_duas_vias.py", "q3_6_cluster.py"]),
    "03": ("03-religion-and-domestic-violence", [
        "00_agrega_sinan.py", "01_monta_base.py", "q4_checks.py", "02_analise.py",
        "03_refino_denominador.py"]),
    "04": ("04-fund-selection", ["02_checks.py", "03_analysis.py"]),
}


def run(script: Path) -> None:
    print(f"\n{'=' * 70}\n>>> {script.relative_to(ROOT)}\n{'=' * 70}", flush=True)
    result = subprocess.run([sys.executable, str(script)], cwd=script.parent.parent, env=ENV)
    if result.returncode != 0:
        sys.exit(f"FAILED: {script.relative_to(ROOT)}")


def table_files() -> list[Path]:
    return sorted(p for p in PAPERS.glob("0[1-3]-*/output/**/*")
                  if p.suffix == ".tex" or p.name == "_stats.txt")


def digest(p: Path) -> str:
    # normalise line endings so a checkout with CRLF does not count as a change
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def verify() -> bool:
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    current = {p.relative_to(ROOT).as_posix(): digest(p) for p in table_files()}
    changed = [k for k in snap if current.get(k) != snap[k]]
    print(f"\nTables identical to the submitted version: {len(snap) - len(changed)}/{len(snap)}")
    for k in changed:
        print(f"  CHANGED: {k}")
    return not changed


if __name__ == "__main__":
    args = [a.lower() for a in sys.argv[1:]]
    if "--snapshot" in args:  # maintainer only: freeze the current tables as the reference
        SNAPSHOT.write_text(json.dumps({p.relative_to(ROOT).as_posix(): digest(p) for p in table_files()},
                                       indent=1), encoding="utf-8")
        sys.exit(f"Snapshot written: {SNAPSHOT.relative_to(ROOT)}")
    if "--verify" in args:
        sys.exit(0 if verify() else 1)
    chosen = [a for a in args if a in STEPS] or list(STEPS)
    for key in chosen:
        folder, steps = STEPS[key]
        code = PAPERS / folder / "code"
        if "--download" in args and key in ("01", "04"):
            steps = [{"01": "q2_1_baixa_series.py", "04": "01_fetch_and_build.py"}[key]] + steps
        for s in steps:
            run(code / s)
    if "--download" not in args and not verify():
        sys.exit("Some tables differ from the submitted version.")
    if "--review" in args:
        run(ROOT / "aecon" / "review.py")
        run(PAPERS / "04-fund-selection" / "code" / "04_memo.py")
    print("\nAll done. Tables and figures in papers/*/output, data checks in papers/*/output/data_checks.json.")

"""Run every paper end to end: base -> data checks -> models -> tables -> final-reports/<paper>.pdf.

    python run_all.py                 # all papers, from the shipped data
    python run_all.py 01 03           # some papers
    python run_all.py --download      # pull the data again first (changes the numbers)
    python run_all.py --review        # also the AI reviewer and the committee memo (recorded answers without a key)
    python run_all.py --verify        # only compare the tables on disk with the snapshot

Each paper lists its scripts, in order, in papers/<paper>/pipeline.txt. A data check marked FAIL stops the run.
The tables of papers 01-02 in the snapshot are the versions submitted for grading.
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
# UTF-8 on Windows consoles; fixed dates so figures and PDFs are byte-identical between runs
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "SOURCE_DATE_EPOCH": "0"}


def papers() -> dict[str, Path]:
    return {p.name[:2]: p for p in sorted(PAPERS.glob("0*-*")) if (p / "pipeline.txt").exists()}


def steps(paper: Path, download: bool) -> list[str]:
    out = []
    for line in (paper / "pipeline.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line.startswith("download:"):
            if download:
                out.append(line.split(":", 1)[1].strip())
        elif line:
            out.append(line)
    return out


def run(script: Path, *args: str) -> None:
    print(f"\n{'=' * 70}\n>>> {script.relative_to(ROOT)} {' '.join(args)}\n{'=' * 70}", flush=True)
    result = subprocess.run([sys.executable, str(script), *args], cwd=script.parent.parent, env=ENV)
    if result.returncode != 0:
        sys.exit(f"FAILED: {script.relative_to(ROOT)}")


def table_files() -> list[Path]:
    return sorted(p for p in PAPERS.glob("0*-*/output/**/*") if p.suffix == ".tex" or p.name.startswith("_"))


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()  # CRLF checkouts count as equal


def verify() -> bool:
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    current = {p.relative_to(ROOT).as_posix(): digest(p) for p in table_files()}
    changed = [k for k in snap if current.get(k) != snap[k]]
    graded = [k for k in snap if k.startswith(("papers/01-", "papers/02-"))]
    print(
        f"\nTables identical to the snapshot: {len(snap) - len(changed)}/{len(snap)} "
        f"({len(graded) - len([k for k in changed if k in graded])}/{len(graded)} graded tables of papers 01-02)"
    )
    for k in changed:
        print(f"  CHANGED: {k}")
    return not changed


if __name__ == "__main__":
    args = [a.lower() for a in sys.argv[1:]]
    if "--snapshot" in args:  # maintainer only: freeze the current tables as the reference
        snap = {p.relative_to(ROOT).as_posix(): digest(p) for p in table_files()}
        SNAPSHOT.write_text(json.dumps(snap, indent=1), encoding="utf-8")
        sys.exit(f"Snapshot written: {SNAPSHOT.relative_to(ROOT)}")
    if "--verify" in args:
        sys.exit(0 if verify() else 1)
    chosen = [k for k in papers() if k in args] or list(papers())
    for key in chosen:
        paper = papers()[key]
        for s in steps(paper, "--download" in args):
            run(paper / "code" / s)
        run(ROOT / "applied_econometrics" / "report.py", key)
    if "--download" not in args and not verify():
        sys.exit("Some tables differ from the snapshot.")
    if "--review" in args:
        run(ROOT / "applied_econometrics" / "review.py")
        run(PAPERS / "04-fund-selection" / "code" / "04_memo.py")
    print("\nDone. Reports in final-reports/; tables, figures and data checks in papers/*/output.")

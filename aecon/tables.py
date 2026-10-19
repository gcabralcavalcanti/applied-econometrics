"""Extract every number from the LaTeX tables (and _stats.txt) of a paper into a flat list of facts.

A fact is one table cell: {"id", "table", "row", "column", "text", "value", "relation", "stars", "kind"}.
The reviewer sends these facts to the model and then re-checks the model's matches here, in Python,
so a number is never declared correct on the model's word alone.
"""
from __future__ import annotations

import re
from pathlib import Path

GREEK = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "pi": "π", "sigma": "σ", "varepsilon": "ε",
         "epsilon": "ε", "geq": "≥", "leq": "≤"}
_NUM = re.compile(r"[-−]?\d[\d.,]*(?:[eE][-+]?\d+)?")


def _clean(cell: str) -> str:
    """LaTeX cell -> plain text (keeps digits, signs, stars and '<')."""
    s = re.sub(r"\\\[-?[\d.]+ex\]", "", cell)          # stargazer spacing \\[-1.8ex]
    s = re.sub(r"\[-?[\d.]+ex\]", "", s)
    s = re.sub(r"\\multicolumn\{\d+\}\{[^}]*\}\{(.*)\}", r"\1", s)
    s = re.sub(r"\\(?:textit|textbf|emph|text|mathrm)\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\^\{(\**)\}", r"\1", s)              # 0.398$^{***}$ -> 0.398***
    s = s.replace("$<$", "<").replace("$>$", ">").replace("\\geq", ">=")
    s = re.sub(r"\\[`'^~\"]\{?([A-Za-z])\}?", r"\1", s)  # \'i -> i
    s = re.sub(r"\\c\{(\w)\}|\\c (\w)", lambda m: m.group(1) or m.group(2), s)
    for cmd, ch in GREEK.items():
        s = re.sub(r"\\" + cmd + r"(?![a-zA-Z])", ch, s)
    s = s.replace("\\%", "%").replace("\\$", "$").replace("\\,", " ").replace("\\ ", " ").replace("\\!", "")
    s = s.replace("\\:", " ").replace("---", "—").replace("--", "–")
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)               # remaining commands (\hline, \cr ...)
    s = s.replace("$", "").replace("{", "").replace("}", "").replace("!", "")
    return re.sub(r"\s+", " ", s).strip().rstrip("\\").strip()


def parse_number(text: str, decimal_comma: bool = False):
    """First number in a cell -> (value, relation, stars, decimals). None if there is no number."""
    t = text.replace("−", "-")
    m = _NUM.search(t)
    if not m:
        return None
    raw = m.group(0).rstrip(".,")
    if decimal_comma:
        raw = raw.replace(".", "").replace(",", ".")
    else:
        raw = raw.replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        return None
    mant, _, exp = raw.lower().partition("e")
    decimals = (len(mant.split(".")[1]) if "." in mant else 0) - (int(exp) if exp else 0)
    relation = "<" if "<" in t[: m.start()] else ">" if ">" in t[: m.start()] else "="
    stars = len(re.search(r"\**", t[m.end():]).group(0)) if t[m.end():].startswith("*") else 0
    return value, relation, stars, decimals


def _is_data(cell: str) -> bool:
    """A cell that holds a result (number, (SE), <0.001), not a header like '(1)' or 'Conclusao (5%)'."""
    return bool(re.match(r"^[(<>\-−]?\s*\d", cell)) and not re.fullmatch(r"\(\d\)", cell)


def _rows(tex: str) -> list[list[str]]:
    body = tex
    if "\\begin{tabular}" in tex:
        body = tex.split("\\begin{tabular}", 1)[1].split("\\end{tabular}", 1)[0]
        spec = re.match(r"\s*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}", body)   # column spec, nested braces
        body = body[spec.end():] if spec else body
    rows = []
    for line in re.split(r"\\\\", body):
        line = re.sub(r"\\(?:hline|toprule|midrule|bottomrule)|\\cline\{[^}]*\}|\\\[-?[\d.]+ex\]", "", line)
        if not line.strip() or "Note:" in line:
            continue
        cells = [_clean(c) for c in re.split(r"(?<!\\)&", line)]
        if any(cells):
            rows.append(cells)
    return rows


def extract_table(path: Path) -> list[dict]:
    tex = path.read_text(encoding="utf-8")
    decimal_comma = len(re.findall(r"\d,\d", tex)) > len(re.findall(r"\d\.\d", tex))
    cap = re.search(r"\\caption\{(.*?)\}(?:\\label|\s*$)", tex, flags=re.M | re.S)
    caption = _clean(cap.group(1)) if cap else ""
    rows = _rows(tex)
    numeric = [any(_is_data(c) for c in r[1:]) for r in rows]
    first_data = next((i for i, n in enumerate(numeric) if n), 0)
    headers = rows[:first_data]
    facts, last_label = [], ""
    for i, row in enumerate(rows[first_data:], start=first_data):
        label = row[0]
        kind = "value"
        if not label:
            label, kind = f"{last_label} (std. error)", "se"
        else:
            last_label = label
        for j, cell in enumerate(row[1:], start=1):
            parsed = parse_number(cell, decimal_comma) if _is_data(cell) else None
            if not parsed:
                continue
            col = " ".join(h[j] for h in headers if j < len(h) and h[j]).strip() or f"column {j}"
            value, relation, stars, decimals = parsed
            facts.append({"table": path.stem, "caption": caption, "row": label, "column": col, "text": cell, "value": value,
                          "relation": relation, "stars": stars, "decimals": decimals,
                          "kind": "se" if kind == "se" or cell.startswith("(") else "value"})
    return facts


def extract_stats(path: Path) -> list[dict]:
    facts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        key, _, val = line.partition("=")
        parsed = parse_number(val)
        if parsed:
            value, relation, stars, decimals = parsed
            facts.append({"table": path.stem, "row": key, "column": "value", "text": val, "value": value,
                          "relation": relation, "stars": 0, "decimals": decimals, "kind": "value"})
    return facts


def paper_facts(paper_dir: Path) -> list[dict]:
    facts = []
    for p in sorted(paper_dir.glob("output/**/*.tex")):
        facts += extract_table(p)
    for p in sorted(paper_dir.glob("output/**/_*.txt")):
        facts += extract_stats(p)
    for i, f in enumerate(facts, start=1):
        f["id"] = f"F{i}"
    return facts


def same_number(text_value: float, text_decimals: int, fact: dict) -> bool:
    """True if a number written in the text is the table number, up to the rounding shown on either side."""
    tol = 0.5 * 10 ** -min(text_decimals, fact["decimals"]) + 1e-12
    if fact["relation"] == "<":                       # table says "<0.001": text must not claim more
        return text_value <= fact["value"] + tol
    return abs(text_value - fact["value"]) <= tol

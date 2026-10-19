"""AI reviewer: does every number in the write-up match the tables, and is each coefficient read correctly?

Division of labour:
  Python  extracts every number from the tables (applied_econometrics.tables) and splits the text into statements;
  model   maps each number in a statement to a table cell and judges the interpretation;
  Python  re-checks every mapped number against the cell, so a "match" never rests on the model alone.

    python -m applied_econometrics.review           # review each paper README's Result section, score the golden set
    python -m applied_econometrics.review --demo    # recorded answers only (no API key, no cost)

Outputs: papers/<paper>/output/review.json and .md, tests/golden/score.json and answers.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from applied_econometrics import config  # noqa: E402
from applied_econometrics.llm import LLM, load_schema  # noqa: E402
from applied_econometrics.tables import paper_facts, parse_number, same_number  # noqa: E402

PAPERS = {
    "01-phillips-curve": (
        "Monthly data for Brazil, 2012-03 to 2026-04. Dependent variable: monthly IPCA inflation (% per month). "
        "OLS. Static model: inflation on unemployment. Dynamic model adds lagged inflation (inertia, gamma) and "
        "the Focus survey expectation for t+1 (delta). Newey-West (HAC) errors change standard errors, never "
        "coefficients. The design is descriptive, not causal."
    ),
    "02-crime-panel": (
        "Panel of 90 North Carolina counties, 1981-1987 (N = 630). Dependent variable: log crime rate; the "
        "deterrence variables and police per capita are in logs, so coefficients are elasticities (a 1% change "
        "in X goes with a beta% change in crime). Pooled OLS, county fixed effects, two-way fixed effects, "
        "county-clustered errors (clustering changes standard errors only). Observational data: police and "
        "arrests respond to crime (simultaneity), so coefficients are associations, not causal effects."
    ),
    "03-religion-and-domestic-violence": (
        "Cross-section of 5,030 Brazilian municipalities, 2011-2013 average. Dependent variable: recorded "
        "domestic violence against women per 1,000 residents (SINAN notifications). Evangelical density is the "
        "% of residents who are evangelical (Census 2010). OLS with state fixed effects and HC1 errors; WLS; "
        "robustness columns (UF = state; 'Cluster UF' = errors clustered by state); "
        "Poisson with a population offset, where IRR = exp(coefficient) multiplies the expected rate per "
        "one-point change. The design is associational, not causal."
    ),
    "04-fund-selection": (
        "Brazilian retail funds (CVM open data), menus of December 2021-2024, next-year returns 2022-2025. "
        "Excess return = fund return net of all fees minus the CDI, in percentage points per year. Persistence: "
        "next-year excess by quintile of this year's excess (Q5 = best) and the slope of next on this year. "
        "Costs: slope of next-year net excess on the expense ratio (% of net assets); -1 = fees are a pure cost. "
        "Monte Carlo: wealth after 10 years relative to staying in the CDI (1.00 = same). Associational, 2021-2025."
    ),
}

SYSTEM = (Path(__file__).parent / "prompts" / "review_system.txt").read_text(encoding="utf-8")


# ------------------------------------------------------------------ statements
def result_section(readme: Path) -> str:
    text = readme.read_text(encoding="utf-8")
    m = re.search(r"^## Result\s*$(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return m.group(1).strip() if m else ""


def split_statements(section: str) -> list[str]:
    """Sentences, bullets and table rows that contain a digit."""
    out, header = [], None
    for line in section.splitlines():
        line = line.strip()
        if not line or set(line) <= set("|-: "):
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if header is None:
                header = cells
                continue
            line = "; ".join(f"{h}: {c}" for h, c in zip(header, cells, strict=False) if c)
            out.append(line)
            continue
        header = None
        line = line.lstrip("-* ").replace("**", "")
        out += [s for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", line) if re.search(r"\d", s)]
    return out


# ------------------------------------------------------------------ the review
def _norm(s: str) -> str:
    return s.replace("−", "-").replace("–", "-").replace(" ", "").replace(",", "")


def _facts_block(facts: list[dict]) -> str:
    lines, current = [], None
    for f in facts:
        if f["table"] != current:
            current = f["table"]
            lines.append(f"## {current}" + (f": {f['caption']}" if f.get("caption") else ""))
        lines.append(f"{f['id']} | {f['row']} | {f['column']} | {f['text']}")
    return "\n".join(lines)


def review(llm: LLM, paper: str, statements: list[dict], task: str) -> list[dict]:
    """statements: [{"id", "text"}]. Returns one adjudicated verdict per statement."""
    facts = paper_facts(config.PAPERS / paper)
    by_id = {f["id"]: f for f in facts}
    ids = [s["id"] for s in statements]
    prompt = f"PAPER DESIGN\n{PAPERS[paper]}\n\nFACTS\n{_facts_block(facts)}\n\nSTATEMENTS\n" + "\n".join(
        f"{s['id']}: {s['text']}" for s in statements
    )

    def check(answer: dict) -> list[str]:
        problems = []
        got = [s["id"] for s in answer["statements"]]
        if got != ids:
            problems.append(f"statement ids must be exactly {ids}, in order")
        for s in answer["statements"]:
            for n in s["numbers"]:
                if n["fact_id"] and n["fact_id"] not in by_id:
                    problems.append(f"{s['id']}: unknown fact id {n['fact_id']}")
        return problems

    answer = llm.ask(task, SYSTEM, prompt, load_schema("review"), check)
    verdicts = []
    for s, a in zip(statements, answer["statements"], strict=True):
        numbers = []
        for n in a["numbers"]:
            fact = by_id.get(n["fact_id"])
            in_text = _norm(n["text_value"]).lstrip("-") in _norm(s["text"])
            if not in_text:
                if n["verdict"] == "mismatch" and fact:
                    # the model quoted the table value instead of the text, but it says the text differs
                    numbers.append(
                        {
                            "text_value": n["text_value"],
                            "fact_id": fact["id"],
                            "table_value": fact["text"],
                            "where": f"{fact['table']} / {fact['row']} / {fact['column']}",
                            "status": "mismatch",
                            "note": "reported by the model (it quoted the table value)",
                        }
                    )
                continue  # otherwise a number the model took from the tables, not from the statement: ignored
            parsed = parse_number(n["text_value"])
            signed = re.search(r"[-−]\s?" + re.escape(n["text_value"].lstrip("-−")), s["text"])
            if parsed and fact and not signed:
                # the statement writes the magnitude ("0.735 points less", "lowers crime by 0.360"): compare
                # magnitudes; the direction is the interpretation check's job
                parsed = (abs(parsed[0]), *parsed[1:])
            if fact and parsed:

                def holds(f, parsed=parsed, signed=signed):
                    return same_number(parsed[0], parsed[3], f if signed else {**f, "value": abs(f["value"])})

                ok, note = holds(fact), ""
                base = fact["row"].replace(" (std. error)", "")
                if not ok:
                    # a slip to the neighbouring cell of the same variable and model (coefficient <-> its SE)
                    alt = next(
                        (
                            f
                            for f in facts
                            if f["table"] == fact["table"]
                            and f["column"] == fact["column"]
                            and f["row"].replace(" (std. error)", "") == base
                            and holds(f)
                        ),
                        None,
                    )
                    if alt is None and n["verdict"] == "match":
                        # the model said "match" but pointed at a cell that does not hold the number: accept only
                        # the same row in another column (a column slip), otherwise Python overrides the model
                        alt = next(
                            (f for f in facts if f["row"] == fact["row"] and f["kind"] == fact["kind"] and holds(f)),
                            None,
                        )
                    if alt is not None:
                        note = f"remapped from {fact['id']} to the neighbouring cell {alt['id']}"
                        ok, fact = True, alt
                status = "match" if ok else "mismatch"
                if not note and status != n["verdict"]:
                    note = f"python overrides model ({n['verdict']})"
            else:
                status, note = "unverified", ""
            numbers.append(
                {
                    "text_value": n["text_value"],
                    "fact_id": fact["id"] if fact else n["fact_id"],
                    "table_value": fact["text"] if fact else None,
                    "where": f"{fact['table']} / {fact['row']} / {fact['column']}" if fact else None,
                    "status": status,
                    "note": note,
                }
            )
        verdicts.append(
            {
                "id": s["id"],
                "text": s["text"],
                "numbers_verdict": "error" if any(n["status"] == "mismatch" for n in numbers) else "ok",
                "interpretation": a["interpretation"],
                "reason": a["reason"],
                "numbers": numbers,
            }
        )
    return verdicts


# ------------------------------------------------------------------ golden set
def score_golden(results: dict[str, list[dict]]) -> dict:
    golden = json.loads((config.GOLDEN / "statements.json").read_text(encoding="utf-8"))
    rows, tp, fn, fp, tn = [], 0, 0, 0, 0
    for paper, items in golden.items():
        got = {v["id"]: v for v in results[paper]}
        for g in items:
            v = got[g["id"]]
            planted = g["expected_numbers"] == "error" or g["expected_interpretation"] == "wrong"
            flagged = v["numbers_verdict"] == "error" or v["interpretation"] == "wrong"
            right_kind = (g["expected_numbers"] != "error" or v["numbers_verdict"] == "error") and (
                g["expected_interpretation"] != "wrong" or v["interpretation"] == "wrong"
            )
            tp += planted and flagged and right_kind
            fn += planted and not (flagged and right_kind)
            fp += (not planted) and flagged
            tn += (not planted) and not flagged
            rows.append(
                {
                    "id": g["id"],
                    "planted": g.get("planted", ""),
                    "expected_flag": planted,
                    "flagged": flagged,
                    "correct": (flagged and right_kind) if planted else not flagged,
                }
            )
    return {
        "planted_errors": tp + fn,
        "caught": tp,
        "missed": fn,
        "clean_statements": fp + tn,
        "false_alarms": fp,
        "catch_rate": round(tp / max(tp + fn, 1), 3),
        "false_alarm_rate": round(fp / max(fp + tn, 1), 3),
        "items": rows,
    }


# ------------------------------------------------------------------ reports
def write_md(paper: str, verdicts: list[dict], path: Path) -> None:
    lines = [
        f"# Reviewer report: {paper}",
        "",
        "Each statement of the README *Result* section, checked against the paper's tables.",
        "",
        "| # | Statement | Numbers | Interpretation | Note |",
        "|---|---|---|---|---|",
    ]
    for v in verdicts:
        nums = (
            "; ".join(
                f"{n['text_value']} → {n['status']}" + (f" ({n['table_value']})" if n["status"] == "mismatch" else "")
                for n in v["numbers"]
            )
            or "—"
        )
        lines.append(
            f"| {v['id']} | {v['text'].replace('|', '/')} | {nums} | {v['interpretation']} | "
            f"{v['reason'].replace('|', '/')} |"
        )
    flagged = [v["id"] for v in verdicts if v["numbers_verdict"] == "error" or v["interpretation"] == "wrong"]
    lines += ["", "## Flags and the author's answer", ""]
    lines += [f"- **{i}**: not answered yet" for i in flagged] or ["No flags."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(mode: str = "auto") -> dict:
    llm = LLM(mode=mode)
    golden = json.loads((config.GOLDEN / "statements.json").read_text(encoding="utf-8"))
    golden_results, summary = {}, {}
    for paper in PAPERS:
        sts = split_statements(result_section(config.PAPERS / paper / "README.md"))
        statements = [{"id": f"S{i}", "text": t} for i, t in enumerate(sts, start=1)]
        verdicts = review(llm, paper, statements, f"review-{paper[:2]}")
        (config.PAPERS / paper / "output" / "review.json").write_text(
            json.dumps(verdicts, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        write_md(paper, verdicts, config.PAPERS / paper / "output" / "review.md")
        flagged = [v["id"] for v in verdicts if v["numbers_verdict"] == "error" or v["interpretation"] == "wrong"]
        unverified = sum(n["status"] == "unverified" for v in verdicts for n in v["numbers"])
        checked = sum(n["status"] != "unverified" for v in verdicts for n in v["numbers"])
        summary[paper] = {
            "statements": len(verdicts),
            "numbers_checked": checked,
            "numbers_not_in_tables": unverified,
            "flagged": flagged,
        }
        if paper not in golden:
            continue
        golden_results[paper] = review(
            llm, paper, [{"id": g["id"], "text": g["text"]} for g in golden[paper]], f"golden-{paper[:2]}"
        )
    score = score_golden(golden_results)
    score["papers"] = summary
    score["llm"] = llm.summary()
    (config.GOLDEN / "score.json").write_text(json.dumps(score, ensure_ascii=False, indent=1), encoding="utf-8")
    (config.GOLDEN / "answers.json").write_text(
        json.dumps(golden_results, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: score[k]
                for k in ("planted_errors", "caught", "false_alarms", "catch_rate", "false_alarm_rate", "papers", "llm")
            },
            indent=1,
        )
    )
    return score


if __name__ == "__main__":
    main("demo" if "--demo" in sys.argv else "live" if "--live" in sys.argv else "auto")

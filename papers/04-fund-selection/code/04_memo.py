"""
04_memo - the AI writes the investment committee memo from the tables, and is checked twice.

  1. Claude (Haiku 5.5) gets every number of the four tables (extracted by Python, with ids) and writes a short memo:
     a recommendation, 3-6 findings, risks and next steps. Every finding must cite the fact ids it uses.
  2. Python rejects the draft (and asks again once) if a finding cites an unknown id or writes a number that is not
     in one of the cells it cites.
  3. The findings then go through the reviewer used for the papers (applied_econometrics.review): numbers re-checked
     against the tables, interpretation judged (causal wording, significance, sign).

    python code/04_memo.py           # live with ANTHROPIC_API_KEY, recorded answer without
Output: output/committee_memo.md, output/committee_memo.json
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent.parent))
from applied_econometrics import review  # noqa: E402
from applied_econometrics.llm import LLM, load_schema  # noqa: E402
from applied_econometrics.tables import paper_facts, parse_number, same_number  # noqa: E402

PAPER = "04-fund-selection"
SYSTEM = """You are the analyst who writes the memo to an investment committee. The committee chooses which retail
funds to offer on a menu (for example a company savings plan) and wants to know two things: does past performance
help to pick funds, and how much do fees cost. You get FACTS: every number in the analysis tables, one per line,
with an id. Write for busy people: plain words, no jargon without a short explanation.

Rules:
- Use only numbers that appear in FACTS, written with the same rounding. After each finding list the fact ids it uses.
- Excess returns are net of all fees and measured against the CDI (the Brazilian overnight rate), in percentage points
  per year. The Monte Carlo reports wealth after 10 years relative to staying in the CDI (1.00 = same).
- The results are associations over 2021-2025, not causal effects; four year pairs is a short history. Say so in the
  risks.
- Recommendation: one or two sentences, a rule the committee can apply.
- 3 to 6 findings, 2 to 4 risks, 1 to 3 next steps."""


def number_problems(memo: dict, by_id: dict) -> list[str]:
    problems = []
    for i, f in enumerate(memo["findings"], start=1):
        unknown = [x for x in f["facts"] if x not in by_id]
        if unknown:
            problems.append(f"finding {i}: unknown fact ids {unknown}")
        cited = [by_id[x] for x in f["facts"] if x in by_id]
        for m in re.finditer(r"[-−]?\d+(?:\.\d+)?", f["text"].replace(",", "")):
            raw = m.group(0)
            if re.fullmatch(r"(19|20)\d\d", raw) or raw in {"10", "1", "2", "3", "4", "5"}:
                continue  # years, the 10-year horizon, quintile and tercile labels
            if any(re.search(rf"(?<![\d.]){re.escape(raw)}(?![\d.])", c.get("caption", "")) for c in cited):
                continue  # stated in the caption of a cited table (e.g. "chance = 20%")
            parsed = parse_number(raw)
            if parsed and not any(
                same_number(parsed[0], parsed[3], c)
                or same_number(abs(parsed[0]), parsed[3], {**c, "value": abs(c["value"])})
                for c in cited
            ):
                problems.append(f"finding {i}: {raw} is not in any of the cells it cites {f['facts']}")
    return problems


def main(mode: str = "auto") -> dict:
    facts = paper_facts(ROOT)
    by_id = {f["id"]: f for f in facts}
    llm = LLM(mode=mode)
    prompt = "FACTS\n" + review._facts_block(facts)
    check = lambda m: number_problems(m, by_id)  # noqa: E731
    memo = llm.ask("memo-04", SYSTEM, prompt, load_schema("memo"), check, 3000)
    rounds = []
    for r in range(2):  # draft, reviewer, at most one revision by the writer, reviewer again
        statements = [{"id": f"M{i}", "text": f["text"]} for i, f in enumerate(memo["findings"], start=1)]
        verdicts = review.review(llm, PAPER, statements, f"memo-review-04-r{r + 1}")
        flags = [
            (s, v)
            for s, v in zip(statements, verdicts, strict=True)
            if v["numbers_verdict"] != "ok" or v["interpretation"] != "ok"
        ]
        rounds.append({"memo": memo, "review": verdicts, "flags": [s["id"] for s, _ in flags]})
        if not flags or r == 1:
            break
        feedback = "\n".join(f'- {s["id"]} "{s["text"]}": {v["reason"]}' for s, v in flags)
        memo = llm.ask(
            "memo-04-revision",
            SYSTEM,
            prompt
            + "\n\nYOUR DRAFT\n"
            + json.dumps(memo, ensure_ascii=False)
            + "\n\nTHE REVIEWER FLAGGED (finding M1 = first finding, and so on)\n"
            + feedback
            + "\n\nRewrite the memo: fix or drop the flagged findings, keep the rest.",
            load_schema("memo"),
            check,
            3000,
        )
    out = {"rounds": rounds, "llm": llm.summary()}
    (ROOT / "output" / "committee_memo.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    lines = [
        "# Memo to the investment committee: picking funds for a retail menu",
        "",
        "*Written by Claude Haiku 5.5 from the tables in this folder; every number was checked by Python against "
        "the cells it cites, then the findings went through the reviewer. Not investment advice.*",
        "",
        f"**Recommendation.** {memo['recommendation']}",
        "",
        "## Findings",
        "",
    ]
    for i, (f, v) in enumerate(zip(memo["findings"], verdicts, strict=True), start=1):
        where = "; ".join(f"{by_id[x]['table']} / {by_id[x]['row']} / {by_id[x]['column']}" for x in f["facts"])
        ok = v["numbers_verdict"] == "ok" and v["interpretation"] == "ok"
        lines.append(
            f"{i}. {f['text']}  \n   *Source: {where}. Reviewer: "
            f"{'numbers and reading OK' if ok else 'FLAGGED: ' + v['reason']}*"
        )
    if len(rounds) > 1:
        first = rounds[0]
        lines += [
            "",
            "## How the draft changed",
            "",
            f"The reviewer flagged {len(first['flags'])} finding(s) in the first draft; the writer revised once.",
        ]
        for v in first["review"]:
            if v["id"] in first["flags"]:
                lines.append(f'- Draft {v["id"]}: "{v["text"]}" → {v["reason"]}')
    lines += ["", "## Risks", ""] + [f"- {r}" for r in memo["risks"]]
    lines += ["", "## Next steps", ""] + [f"- {s}" for s in memo["next_steps"]]
    (ROOT / "output" / "committee_memo.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    flagged = [v["id"] for v in verdicts if v["numbers_verdict"] != "ok" or v["interpretation"] != "ok"]
    print(f"Memo: {len(memo['findings'])} findings, flagged by the reviewer: {flagged or 'none'}; {llm.summary()}")
    return out


if __name__ == "__main__":
    main("demo" if "--demo" in sys.argv else "auto")

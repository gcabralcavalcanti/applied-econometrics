"""The reviewer, without spending anything: recorded answers (demo mode) and a fake model."""

import json

import pytest

from applied_econometrics import config, review
from applied_econometrics.llm import LLM, BudgetExceeded, NoRecording, load_schema


class FakeLLM:
    """Returns a canned answer after running the same schema validation and checker as the real client."""

    def __init__(self, answer):
        self.answer = answer
        self.problems = None

    def ask(self, task, system, prompt, schema, check=None, max_tokens=0):
        import jsonschema

        jsonschema.validate(self.answer, schema)
        self.problems = check(self.answer) if check else []
        return self.answer


ST = [{"id": "S1", "text": "In the dynamic model, lagged inflation has a coefficient of 0.389."}]


def _fact_id(row_part, col_part, table="q2_tab_phillips_dinamica"):
    from applied_econometrics.tables import paper_facts

    return next(
        f["id"]
        for f in paper_facts(config.PAPERS / "01-phillips-curve")
        if f["table"] == table and row_part in f["row"] and col_part in f["column"]
    )


def _answer(value, fact_id, verdict):
    return {
        "statements": [
            {
                "id": "S1",
                "numbers": [{"text_value": value, "fact_id": fact_id, "verdict": verdict}],
                "interpretation": "ok",
                "reason": "test",
            }
        ]
    }


def test_python_overrides_a_wrong_match_from_the_model():
    fid = _fact_id("Inflação defasada", "Dinâmica")
    v = review.review(FakeLLM(_answer("0.389", fid, "match")), "01-phillips-curve", ST, "t")[0]
    assert v["numbers_verdict"] == "error"
    assert "overrides" in v["numbers"][0]["note"]


def test_numbers_not_in_the_statement_are_ignored():
    """The model may quote the table value instead of the text; only numbers written in the statement count."""
    fake = FakeLLM(_answer("0.398", _fact_id("Inflação defasada", "Dinâmica"), "match"))
    v = review.review(fake, "01-phillips-curve", ST, "t")[0]
    assert v["numbers"] == [] and v["numbers_verdict"] == "ok"


def test_checker_rejects_unknown_fact_ids():
    fake = FakeLLM(_answer("0.389", "F99999", "match"))
    review.review(fake, "01-phillips-curve", ST, "t")
    assert any("unknown fact id" in p for p in fake.problems)


def test_split_statements_reads_bullets_and_table_rows():
    text = "| Spec | b |\n|---|---|\n| OLS | -0.6 |\n\n- First 0.1 here. Second 0.2 there.\n- No digits."
    assert review.split_statements(text) == ["Spec: OLS; b: -0.6", "First 0.1 here.", "Second 0.2 there."]


def test_golden_set_from_recorded_answers():
    """Demo mode: replays the recorded live run, so the score in the README is reproducible for free."""
    score = review.main(mode="demo")
    assert score["llm"]["api_calls"] == 0
    assert score["planted_errors"] == 18
    assert score["caught"] == 18
    assert score["false_alarms"] == 0


def test_recordings_match_the_schema():
    schema = load_schema("review")
    import jsonschema

    files = list(config.RECORDINGS.glob("*.json"))
    assert len(files) >= 9  # 4 paper reviews, 3 golden batches, the memo and its review
    memo_schema = load_schema("memo")
    for p in files:
        answer = json.loads(p.read_text(encoding="utf-8"))["answer"]
        jsonschema.validate(answer, memo_schema if p.name.startswith("memo-04-") and "review" not in p.name else schema)


def test_demo_mode_never_calls_the_api(tmp_path):
    llm = LLM(mode="demo", recordings=tmp_path, log_dir=tmp_path)
    with pytest.raises(NoRecording):
        llm.ask("x", "system", "prompt", {"type": "object"})


def test_call_cap(tmp_path):
    llm = LLM(mode="demo", max_calls=0, recordings=tmp_path, log_dir=tmp_path)
    with pytest.raises(BudgetExceeded):
        llm._call("s", "u", {}, 10)


def test_memo_numbers_must_be_in_the_cited_cells():
    import importlib.util

    spec = importlib.util.spec_from_file_location("memo", config.PAPERS / "04-fund-selection" / "code" / "04_memo.py")
    memo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(memo)
    from applied_econometrics.tables import paper_facts

    facts = {f["id"]: f for f in paper_facts(config.PAPERS / "04-fund-selection")}
    eq = next(
        i
        for i, f in facts.items()
        if f["table"] == "tab_costs" and f["row"] == "Expense ratio (slope)" and f["column"] == "Equity"
    )
    good = {"findings": [{"text": "Each point of fees goes with 0.735 points less return.", "facts": [eq]}]}
    bad = {"findings": [{"text": "Each point of fees goes with 0.835 points less return.", "facts": [eq]}]}
    assert memo.number_problems(good, facts) == []
    assert memo.number_problems(bad, facts)


def test_memo_replays_without_a_key():
    import importlib.util

    spec = importlib.util.spec_from_file_location("memo", config.PAPERS / "04-fund-selection" / "code" / "04_memo.py")
    memo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(memo)
    out = memo.main("demo")
    assert out["llm"]["api_calls"] == 0
    assert out["rounds"][-1]["flags"] == []

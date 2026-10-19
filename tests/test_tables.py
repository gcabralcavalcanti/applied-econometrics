import importlib.util
import json

import pytest

from applied_econometrics import config
from applied_econometrics.tables import paper_facts, parse_number, same_number


@pytest.mark.parametrize(
    "text,comma,expected",
    [
        ("0.398$^{***}$".replace("$^{***}$", "***"), False, (0.398, "=", 3, 3)),
        ("-0,360***", True, (-0.360, "=", 3, 3)),
        ("(0,064)", True, (0.064, "=", 0, 3)),
        ("<0.001", False, (0.001, "<", 0, 3)),
        ("7.59e-06", False, (7.59e-06, "=", 0, 8)),
        ("12,430.15", False, (12430.15, "=", 0, 2)),
        ("−0.0077", False, (-0.0077, "=", 0, 4)),
    ],
)
def test_parse_number(text, comma, expected):
    assert parse_number(text, comma) == pytest.approx(expected)


def test_same_number_uses_the_rounding_shown():
    fact = {"value": -0.002, "decimals": 3, "relation": "="}
    assert same_number(-0.0024, 4, fact)  # text more precise than the table
    assert not same_number(-0.004, 3, fact)
    assert same_number(0.0009, 4, {"value": 0.001, "decimals": 3, "relation": "<"})
    assert not same_number(0.389, 3, {"value": 0.398, "decimals": 3, "relation": "="})


def _cell(paper, table, row_part, col_part):
    return next(
        f
        for f in paper_facts(config.PAPERS / paper)
        if f["table"] == table and row_part in f["row"] and col_part in f["column"]
    )


def test_extracts_known_cells():
    assert _cell("01-phillips-curve", "q2_tab_phillips_dinamica", "Inflação defasada", "Dinâmica")["value"] == 0.398
    se = _cell("02-crime-panel", "q3_tab_cluster", "prisao) β_1 (std. error)", "Cluster")
    assert se["value"] == 0.064 and se["kind"] == "se"
    assert _cell("03-religion-and-domestic-violence", "tab_poisson", "Densidade", "IRR")["value"] == 1.0081
    assert _cell("03-religion-and-domestic-violence", "_stats", "evang_M1_p", "value")["value"] == 0.325


def test_tables_identical_to_submitted_version():
    spec = importlib.util.spec_from_file_location("run_all", config.ROOT / "run_all.py")
    run_all = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_all)
    snapshot = json.loads(run_all.SNAPSHOT.read_text(encoding="utf-8"))
    assert len([k for k in snapshot if k.startswith(("papers/01-", "papers/02-"))]) == 13
    assert run_all.verify()


def test_final_reports_are_built_from_the_outputs():
    from applied_econometrics import report

    for paper in report.MAIN:
        out = report.build(paper)
        first = out.read_bytes()
        assert first[:4] == b"%PDF" and len(first) > 20_000
        assert report.build(paper).read_bytes() == first  # same outputs -> same PDF

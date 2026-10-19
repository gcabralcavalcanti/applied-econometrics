import json

import pandas as pd
import pytest

from applied_econometrics import config
from applied_econometrics.checks import FAIL, PASS, WARN, Report


def test_report_statuses_and_exit(tmp_path):
    r = Report("demo", [])
    df = pd.DataFrame({"date": pd.to_datetime(["2020-01-01", "2020-02-01", "2020-04-01"]), "x": [1.0, None, 50.0]})
    r.no_missing(df, ["x"])
    r.monthly_continuity(df["date"], "x")
    r.in_range(df["x"].dropna(), 0, 10, "x", "%", WARN)
    statuses = [c["status"] for c in r.results]
    assert statuses == [FAIL, FAIL, WARN]
    with pytest.raises(SystemExit):
        r.finish(tmp_path / "checks.json")
    saved = json.loads((tmp_path / "checks.json").read_text(encoding="utf-8"))
    assert saved["summary"] == {PASS: 0, WARN: 1, FAIL: 2}


@pytest.mark.parametrize(
    "paper,warns",
    [
        ("01-phillips-curve", 1),
        ("02-crime-panel", 2),
        ("03-religion-and-domestic-violence", 1),
        ("04-fund-selection", 5),
    ],
)
def test_shipped_data_passes_its_checks(paper, warns):
    report = json.loads((config.PAPERS / paper / "output" / "data_checks.json").read_text(encoding="utf-8"))
    assert report["summary"][FAIL] == 0
    assert report["summary"][WARN] == warns
    assert report["inputs"], "input fingerprints are recorded"

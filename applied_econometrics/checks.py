"""Automatic data checks: each paper lists what must be true about its data before any model runs.

A check returns PASS, WARN (worth knowing, does not stop the run) or FAIL (stops the run).
Every run writes output/data_checks.json in the paper folder, with the input fingerprints,
so a reviewer can see which data the published tables came from.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

PASS, WARN, FAIL = "pass", "warn", "fail"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()[:16]


def _plain(x):
    """JSON-friendly version of numpy / pandas values."""
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return None if np.isnan(x) else round(float(x), 6)
    if isinstance(x, (pd.Timestamp,)):
        return str(x.date())
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    return x


class Report:
    def __init__(self, paper: str, inputs: list[Path]):
        self.paper = paper
        self.inputs = inputs
        self.results: list[dict] = []

    # ------------------------------------------------------------ generic checks
    def add(self, name: str, ok: bool, detail: str, value=None, severity: str = FAIL) -> bool:
        self.results.append(
            {"check": name, "status": PASS if ok else severity, "detail": detail, "value": _plain(value)}
        )
        return ok

    def no_missing(self, df: pd.DataFrame, cols: list[str], name: str = "missing values"):
        miss = {c: int(df[c].isna().sum()) for c in cols}
        bad = {c: n for c, n in miss.items() if n}
        return self.add(
            name, not bad, "no missing values in " + ", ".join(cols) if not bad else f"missing values: {bad}", miss
        )

    def no_duplicates(self, df: pd.DataFrame, keys: list[str]):
        n = int(df.duplicated(keys).sum())
        return self.add(f"unique keys ({', '.join(keys)})", n == 0, f"{n} duplicated rows", n)

    def in_range(self, s: pd.Series, lo: float, hi: float, name: str, unit: str, severity: str = FAIL):
        out = s[(s < lo) | (s > hi)]
        return self.add(
            f"range: {name}",
            out.empty,
            f"all {len(s)} values in [{lo}, {hi}] {unit}"
            if out.empty
            else f"{len(out)} of {len(s)} values outside [{lo}, {hi}] {unit} (min {s.min():.4g}, max {s.max():.4g})",
            {"min": s.min(), "max": s.max(), "outside": len(out)},
            severity,
        )

    def monthly_continuity(self, dates: pd.Series, name: str):
        d = pd.to_datetime(dates).dt.to_period("M").sort_values()
        full = pd.period_range(d.iloc[0], d.iloc[-1], freq="M")
        gaps = sorted(set(full) - set(d))
        return self.add(
            f"no gaps in months: {name}",
            not gaps,
            f"{len(d)} months, {d.iloc[0]} to {d.iloc[-1]}, no gaps"
            if not gaps
            else f"missing months: {[str(g) for g in gaps[:12]]}",
            {"first": str(d.iloc[0]), "last": str(d.iloc[-1]), "n": len(d), "gaps": len(gaps)},
        )

    def jumps(self, s: pd.Series, dates: pd.Series, name: str, k: float = 5.0):
        """Flag month-on-month changes larger than k MAD-based SDs (possible breaks or unit changes)."""
        diff = s.diff()
        mad = (diff - diff.median()).abs().median() * 1.4826
        big = diff[(diff - diff.median()).abs() > k * mad] if mad > 0 else diff.iloc[0:0]
        when = [str(pd.Timestamp(dates.loc[i]).date()) for i in big.index]
        return self.add(
            f"large jumps: {name}",
            big.empty,
            f"no change above {k} MAD-based SDs"
            if big.empty
            else f"{len(big)} changes above {k} MAD-based SDs at {when[:8]}",
            when,
            WARN,
        )

    # ------------------------------------------------------------------ output
    def write(self, path: Path) -> dict:
        counts = {s: sum(r["status"] == s for r in self.results) for s in (PASS, WARN, FAIL)}
        report = {
            "paper": self.paper,
            "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "summary": counts,
            "inputs": {str(p.name): sha256(p) for p in self.inputs if p.exists()},
            "checks": self.results,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[checks] {self.paper}: {counts[PASS]} pass, {counts[WARN]} warn, {counts[FAIL]} fail -> {path.name}")
        for r in self.results:
            if r["status"] != PASS:
                print(f"  {r['status'].upper()}: {r['check']} - {r['detail']}")
        return report

    def finish(self, path: Path) -> None:
        report = self.write(path)
        if report["summary"][FAIL]:
            sys.exit(f"Data checks failed for {self.paper}; see {path}")

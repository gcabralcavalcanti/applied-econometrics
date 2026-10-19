"""Paths, model choice and cost limits. Everything that costs money is capped here."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"
RECORDINGS = ROOT / "recordings"   # recorded LLM answers: response cache + demo mode (versioned)
REPORTS = ROOT / "reports"         # reviewer reports (versioned, so the repo shows real output)
LOGS = ROOT / "logs"               # one JSON line per LLM call (not versioned)
SCHEMAS = ROOT / "schemas"
GOLDEN = ROOT / "golden"
CACHE = ROOT / ".cache"            # large downloads (not versioned)

# Cheapest model that handles number matching and short structured judgements.
MODEL = os.environ.get("AECON_MODEL", "claude-haiku-5-5")
PRICE_PER_MTOK = {"claude-haiku-5-5": (0.10, 0.50)}  # USD (input, output), Anthropic price list

# Hard limits per run (the account has a fixed monthly credit and no card on file).
MAX_CALLS_PER_RUN = int(os.environ.get("AECON_MAX_CALLS", "20"))
MAX_TOKENS = 8000         # per answer, thinking included; a review of ~10 statements uses ~1-3k
# Thinking off: on the golden set it caught 16-17 of 18 planted errors across runs; low-effort thinking
# caught 16 at a similar cost, so it is off (reports/experiments/).
THINKING = os.environ.get("AECON_THINKING", "0") == "1"
EFFORT = "low"
TIMEOUT_S = 60.0
SDK_RETRIES = 2           # network/429/5xx retries done by the SDK
SCHEMA_RETRIES = 1        # one extra call if the answer fails our own checks

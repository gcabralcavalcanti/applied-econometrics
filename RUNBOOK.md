# Runbook

## Run

```bash
pip install -r requirements.txt
python run_all.py            # all papers from the shipped data; ends with "Tables identical to the snapshot"
python run_all.py 03         # one paper
python run_all.py --review   # also the AI reviewer and the committee memo (recorded answers without a key)
python -m pytest             # no API calls
```

A data check marked FAIL stops the run before any regression. Read `papers/<paper>/output/data_checks.json`.

## Update the data

```bash
python run_all.py --download   # papers 01, 03 and 04 pull fresh data from the BCB, IBGE and CVM
python run_all.py --verify     # lists the tables that changed
python run_all.py --snapshot   # only after reviewing the changes: makes the new tables the reference
```

New data changes the numbers, so update each paper's README *Result* section and run `--review`; the reviewer flags any
sentence whose number no longer matches a table. Paper 04's raw CVM files (~750 MB) are cached in `.cache/cvm/`.

## When something fails

| Symptom | Cause | What to do |
|---|---|---|
| A download step fails (timeout, HTTP 5xx) | the BCB, IBGE or CVM API is down | rerun later; without `--download` everything runs from the shipped data |
| `FAIL` in a data check | the new data broke an assumption (gap, unit, missing capital) | read the check's detail, fix the input or the code; do not relax the check to make it pass |
| `CHANGED` after `run_all.py` without `--download` | a code change altered a table | find the change; the graded tables of papers 01-02 must stay identical |
| `NoRecording` in the reviewer | the reviewed text changed and there is no API key | set `ANTHROPIC_API_KEY` (or `.env`) and run `--review` once; the new answers are recorded |
| `BudgetExceeded` | more than 20 API calls in one run | raise `APPLIED_ECON_MAX_CALLS` only if the extra calls are expected |

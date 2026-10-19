"""Merge the three raw series into one monthly base for the Phillips-curve regressions.

Modelling choices:
 - inflation is the monthly IPCA (% per month), matching a monthly equation;
 - the expectation is the Focus median for month t+1 in the last survey of month t;
 - the window is the intersection of the three series (PNAD Continua starts in 2012-03).

Inputs:  tmp/q2_ipca.csv, tmp/q2_desemprego.csv, tmp/q2_focus_mensal.csv
Outputs: tmp/q2_base_phillips.csv (data, ipca, desemprego, exp_ipca_prox)
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = ROOT / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

ipca = pd.read_csv(TMP_DIR / "q2_ipca.csv", parse_dates=["Date"]).set_index("Date")
unemployment = pd.read_csv(TMP_DIR / "q2_desemprego.csv", parse_dates=["Date"]).set_index("Date")

# Month start on both indexes, so the joins align.
ipca.index = ipca.index.to_period("M").to_timestamp()
unemployment.index = unemployment.index.to_period("M").to_timestamp()

# Focus has many readings per month. Keep the readings made in month t about month t+1,
# take the last survey of month t, and index it by t so it lines up with pi_t.
focus = pd.read_csv(TMP_DIR / "q2_focus_mensal.csv")
focus["Data"] = pd.to_datetime(focus["Data"])
focus["ref"] = pd.to_datetime(focus["DataReferencia"], format="%m/%Y")
focus["survey_month"] = focus["Data"].dt.to_period("M")
focus["target_month"] = focus["ref"].dt.to_period("M")

one_month_ahead = focus[focus["target_month"] == (focus["survey_month"] + 1)]
last_reading = one_month_ahead.sort_values("Data").groupby("survey_month").tail(1)

expectation = (
    last_reading.assign(data=last_reading["survey_month"].dt.to_timestamp())
    .set_index("data")[["Mediana"]]
    .rename(columns={"Mediana": "exp_ipca_prox"})
)

df = ipca.join(unemployment, how="outer").join(expectation, how="outer").sort_index().dropna()
df.index.name = "data"

df.to_csv(TMP_DIR / "q2_base_phillips.csv")

print("Phillips-curve base built.")
print(f"  Period:  {df.index.min().date()} to {df.index.max().date()}  ({len(df)} months)")
print(f"  Columns: {list(df.columns)}")
print("\nFirst rows:")
print(df.head().to_string())
print("\nLast rows:")
print(df.tail().to_string())
print("\nSaved: tmp/q2_base_phillips.csv")

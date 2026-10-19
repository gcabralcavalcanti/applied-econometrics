"""Download the three raw series from the Central Bank of Brazil APIs.

Inputs:  none (SGS and the Focus expectations API).
Outputs: tmp/q2_ipca.csv, tmp/q2_desemprego.csv, tmp/q2_focus_mensal.csv
"""

from pathlib import Path

from bcb import Expectativas, sgs

ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = ROOT / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# PNAD Continua starts in 2012, so nothing earlier can enter the regression.
START_DATE = "2012-01-01"

# SGS codes: 433 = IPCA, monthly % change; 24369 = unemployment rate, PNAD Continua (%).
print("Downloading IPCA (433) and unemployment (24369) from SGS...")
sgs_df = sgs.get({"ipca": 433, "desemprego": 24369}, start=START_DATE)

ipca = sgs_df[["ipca"]].dropna()
unemployment = sgs_df[["desemprego"]].dropna()

ipca.to_csv(TMP_DIR / "q2_ipca.csv")
unemployment.to_csv(TMP_DIR / "q2_desemprego.csv")
print(f"  IPCA:         {len(ipca):>4} months ({ipca.index.min().date()} to {ipca.index.max().date()})")
print(
    f"  Unemployment: {len(unemployment):>4} months "
    f"({unemployment.index.min().date()} to {unemployment.index.max().date()})"
)

# baseCalculo = 0: statistics over the answers of the last 30 days.
# Every survey date and reference month is kept; q2_2 picks one reading per month.
print("Downloading Focus expectations (monthly IPCA)...")
endpoint = Expectativas().get_endpoint("ExpectativaMercadoMensais")
focus = (
    endpoint.query()
    .filter(endpoint.Indicador == "IPCA")
    .filter(endpoint.baseCalculo == 0)
    .filter(endpoint.Data >= START_DATE)
    .select(endpoint.Indicador, endpoint.Data, endpoint.DataReferencia, endpoint.Mediana, endpoint.Media)
    .collect()
)
focus.to_csv(TMP_DIR / "q2_focus_mensal.csv", index=False)
print(f"  Focus:        {len(focus):>4} rows")

print("\nRaw series saved in tmp/.")

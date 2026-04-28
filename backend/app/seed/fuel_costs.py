"""
Seed provincial fuel and electricity costs.
The Excel has a single row per province (current prices).
We store them for year 2025 and project forward with an annual escalation.
"""
import pandas as pd
from sqlalchemy.orm import Session
from app.models.reference_data import ProvincialFuelCost

FUEL_ESCALATION = 0.03     # 3% annual fuel price increase
ELECTRICITY_ESCALATION = 0.02  # 2% annual electricity increase
PROJECTION_YEARS = range(2025, 2035)


def _parse_float(val):
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except Exception:
        return None


def seed(session: Session, xl: pd.ExcelFile):
    df = xl.parse("Fuel & Electricity Costs table")
    df = df[df["Province"].notna() & df["Province"].apply(lambda x: isinstance(x, str))]

    inserted = 0
    for _, row in df.iterrows():
        province = str(row["Province"]).strip()
        if len(province) > 5 or not province.isupper():
            continue

        elec_2025 = _parse_float(row.get("Cost of electricity ($/kWh)"))
        gas_2025 = _parse_float(row.get("Gasoline cost ($/L)"))
        diesel_2025 = _parse_float(row.get("Diesel cost ($/L)"))

        if elec_2025 is None:
            continue

        for year in PROJECTION_YEARS:
            offset = year - 2025
            elec = elec_2025 * ((1 + ELECTRICITY_ESCALATION) ** offset)
            gas = (gas_2025 or 1.65) * ((1 + FUEL_ESCALATION) ** offset)
            diesel = (diesel_2025 or 1.70) * ((1 + FUEL_ESCALATION) ** offset)

            session.add(ProvincialFuelCost(
                province=province,
                year=year,
                electricity_rate_kwh=elec,
                diesel_price_l=diesel,
                gasoline_price_l=gas,
            ))
            inserted += 1

    print(f"Seeded {inserted} provincial fuel cost rows")

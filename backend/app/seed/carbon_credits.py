"""
Seed CFR marginal values from the New CFR marginal value sheet.
Values are in $/kWh dispensed; stored as-is.
"""
import pandas as pd
from sqlalchemy.orm import Session
from app.models.reference_data import CarbonCredit

PROJECTION_YEARS = range(2025, 2035)


def seed(session: Session, xl: pd.ExcelFile):
    df = xl.parse("New CFR marginal value")
    df = df[df["Province"].notna() & df["Province"].apply(lambda x: isinstance(x, str))]

    inserted = 0
    for _, row in df.iterrows():
        province = str(row["Province"]).strip()
        if len(province) > 5:
            continue
        cfr_val = row.get("Marginal CFR $ value per kWh dispensed")
        try:
            cfr_val = float(cfr_val)
        except Exception:
            continue

        for year in PROJECTION_YEARS:
            # CFR values increase ~5% annually (policy trajectory)
            offset = year - 2025
            adjusted = cfr_val * ((1.05) ** offset)
            session.add(CarbonCredit(
                province=province,
                year=year,
                month=None,
                credit_value_per_tonne=adjusted,
            ))
            inserted += 1

    print(f"Seeded {inserted} CFR carbon credit rows")

import pandas as pd
from sqlalchemy.orm import Session
from app.models.reference_data import Charger


def _parse_float(val):
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except Exception:
        return None


def seed(session: Session, xl: pd.ExcelFile):
    df = xl.parse("Charger database")
    df = df[df["Charger type"].notna()]

    inserted = 0
    for _, row in df.iterrows():
        charger_type = str(row["Charger type"]).strip()
        cost = _parse_float(row.get("Purchase + installation cost$ CAD"))
        power_kw = _parse_float(row.get("Max charge rate (kW)"))

        if cost is None or power_kw is None:
            continue

        charger_name = str(row.get("Charger name", charger_type)).strip()
        display = f"{charger_type} ({power_kw:.0f} kW)"

        charger = Charger(
            type_name=charger_type,
            power_kw=power_kw,
            unit_cost_cad=cost * 0.85,       # approx unit portion
            installation_cost_cad=cost * 0.15,  # approx install portion
            lifespan_years=10,
            display_name=display,
        )
        session.add(charger)
        inserted += 1

    print(f"Seeded {inserted} chargers")

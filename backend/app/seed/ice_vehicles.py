import pandas as pd
from sqlalchemy.orm import Session
from app.models.reference_data import ICEVehicle


def _parse_float(val):
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", "").replace("$", "").strip())
    except Exception:
        return None


def seed(session: Session, xl: pd.ExcelFile):
    df = xl.parse("ICE database")
    df = df[df["Make + Model"].notna() & (df["Make + Model"].astype(str).str.strip() != "")]

    inserted = 0
    for _, row in df.iterrows():
        make_model = str(row["Make + Model"]).strip()
        # Split on first space for make
        parts = make_model.split(" ", 1)
        make = parts[0]
        model = parts[1] if len(parts) > 1 else make_model

        msrp = _parse_float(row.get("Purchase price ($ CAD)"))
        if msrp is None:
            continue

        efficiency_l_per_km = _parse_float(row.get("Efficiency (L/KM)"))
        if efficiency_l_per_km is None:
            continue

        payload = _parse_float(row.get("Payload (lbs)")) or 0.0
        year = _parse_float(row.get("Model Year"))
        category = str(row.get("Category", "Light Duty")).strip()
        fuel_type = str(row.get("Fuel type", "Diesel")).strip()

        # Convert L/km to L/100km for storage
        l_per_100km = efficiency_l_per_km * 100

        vehicle = ICEVehicle(
            make=make,
            model=model,
            year=int(year) if year else None,
            msrp_cad=msrp,
            fuel_type=fuel_type,
            fuel_consumption_l_per_100km=l_per_100km,
            payload_lbs=payload,
            category=category,
            display_name=make_model,
        )
        session.add(vehicle)
        inserted += 1

    print(f"Seeded {inserted} ICE vehicles")

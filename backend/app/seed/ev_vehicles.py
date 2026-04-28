import pandas as pd
from sqlalchemy.orm import Session
from app.models.reference_data import EVVehicle, EVProvincialRebate


PROVINCE_TOTAL_COLS = {
    "ON": "ON - Total rebate(s) value",
    "BC": "BC - Total rebate(s) value",
    "QC": "QC - Total rebate(s) value",
    "AB": "AB - Total rebate(s) value",
    "SC": "SC - Total rebate(s) value",
    "NS": "NS - Total rebate(s) value",
    "NB": "NB - Total rebate(s) value",
    "MB": "MB - Total rebate(s) value",
    "PEI": "PEI - Total rebate(s) value",
    "NL": "NL - Total rebate(s) value",
    "YT": "YT - Total rebate(s) value",
    "NU": "NU - Total rebate(s) value",
    "NT": "NT - Total rebate(s) value",
}


def _parse_float(val):
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", "").replace("$", "").strip())
    except Exception:
        return None


def _parse_battery(val):
    if pd.isna(val):
        return None
    import re
    m = re.search(r"[\d.]+", str(val))
    return float(m.group()) if m else None


def seed(session: Session, xl: pd.ExcelFile):
    df = xl.parse("EV database")

    # Use exact column names as found in Excel
    MAKE_COL = "Manufacturer  "
    MODEL_COL = "Model"
    MSRP_COL = "Cost, $MSRP\nCAD"
    EFF_COL = "Efficiency (kwh/km)"
    RANGE_COL = "Range (km)"
    PAYLOAD_COL = "Max Payload, lbs."
    BATTERY_COL = "Battery Size, kWh"
    CAT_COL = "Category"
    YEAR_COL = "Model Year "
    REFRIG_COL = "Refrigerated Unit"
    IMHZEV_COL = "Federal Rebates (iMHZEV) "

    df = df[df[MAKE_COL].notna() & (df[MAKE_COL].astype(str).str.strip() != "")]

    inserted = 0
    for _, row in df.iterrows():
        make = str(row[MAKE_COL]).strip()
        model = str(row[MODEL_COL]).strip() if pd.notna(row[MODEL_COL]) else ""
        make_model = f"{make} {model}".strip()

        msrp = _parse_float(row[MSRP_COL])
        if msrp is None:
            continue

        efficiency = _parse_float(row[EFF_COL])
        if efficiency is None:
            continue

        range_km = _parse_float(row[RANGE_COL])
        payload = _parse_float(row[PAYLOAD_COL])
        battery = _parse_battery(row[BATTERY_COL])
        category = str(row[CAT_COL]).strip() if pd.notna(row[CAT_COL]) else "Light Duty"
        year_raw = _parse_float(row[YEAR_COL])
        refrig = str(row[REFRIG_COL]).strip().lower() == "yes" if pd.notna(row[REFRIG_COL]) else False
        imhzev = _parse_float(row[IMHZEV_COL])

        ev = EVVehicle(
            make=make,
            model=model,
            year=int(year_raw) if year_raw else None,
            msrp_cad=msrp,
            battery_kwh=battery or 0.0,
            efficiency_kwh_per_km=efficiency,
            range_km=range_km or 0.0,
            payload_lbs=payload or 0.0,
            category=category,
            has_refrigeration=refrig,
            imhzev_rebate_eligible=bool(imhzev and imhzev > 0),
            display_name=make_model,
        )
        session.add(ev)
        session.flush()

        for province, col in PROVINCE_TOTAL_COLS.items():
            rebate_val = _parse_float(row.get(col))
            if rebate_val and rebate_val > 0:
                session.add(EVProvincialRebate(
                    ev_vehicle_id=ev.id,
                    province=province,
                    rebate_amount_cad=rebate_val,
                ))

        inserted += 1

    print(f"Seeded {inserted} EV vehicles")

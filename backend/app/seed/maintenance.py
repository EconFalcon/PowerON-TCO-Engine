"""
Seed maintenance cost rates from the Maintenance costs table sheet.
"""
import pandas as pd
from sqlalchemy.orm import Session
from app.models.reference_data import MaintenanceCost

# Mapping from Excel row labels to our category + type
ROW_MAP = {
    "Light-Duty ICE": ("Light Duty", "ICE"),
    "Light-Duty EVs": ("Light Duty", "EV"),
    "Heavy-Duty ICE": ("Heavy Duty", "ICE"),
    "Heavy-Duty EVs": ("Heavy Duty", "EV"),
    "Medium-Duty ICE": ("Medium Duty", "ICE"),
    "Medium-Duty EVs": ("Medium Duty", "EV"),
}


def seed(session: Session, xl: pd.ExcelFile):
    df = xl.parse("Maintenance costs table", header=None)

    inserted = 0
    for _, row in df.iterrows():
        label = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        if label not in ROW_MAP:
            continue
        category, vehicle_type = ROW_MAP[label]
        try:
            cost_per_km = float(row.iloc[3])  # "Total Cost CA$/km" column
        except Exception:
            continue

        session.add(MaintenanceCost(
            vehicle_category=category,
            vehicle_type=vehicle_type,
            cost_per_km=cost_per_km,
        ))
        inserted += 1

    print(f"Seeded {inserted} maintenance cost rows")

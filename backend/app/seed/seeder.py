"""
Main seeder: reads the PowerOn TCO Excel file and populates the SQLite database.
Run: python -m app.seed.seeder --file <path_to_excel> --db data/tco.db
"""
import argparse
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base


def main():
    parser = argparse.ArgumentParser(description="Seed TCO database from Excel")
    parser.add_argument("--file", required=True, help="Path to TCO Excel file")
    parser.add_argument("--db", default="data/tco.db", help="SQLite DB path")
    args = parser.parse_args()

    db_url = f"sqlite:///{args.db}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # Import models to register them with Base
    from app.models import reference_data, scenario  # noqa

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    xl = pd.ExcelFile(args.file)
    print(f"Sheets in workbook: {xl.sheet_names}")

    with Session() as session:
        from app.seed import ev_vehicles, ice_vehicles, chargers, fuel_costs, maintenance, carbon_credits
        ev_vehicles.seed(session, xl)
        ice_vehicles.seed(session, xl)
        chargers.seed(session, xl)
        fuel_costs.seed(session, xl)
        maintenance.seed(session, xl)
        carbon_credits.seed(session, xl)
        session.commit()

    print("Seeding complete.")


if __name__ == "__main__":
    main()

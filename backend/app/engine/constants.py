# Default constants mirroring the Excel workbook assumptions

ANALYSIS_YEARS = 10

# Tire cost per km by vehicle category and type
TIRE_COST_PER_KM = {
    "Light Duty": {"EV": 0.018, "ICE": 0.023},
    "Medium Duty": {"EV": 0.025, "ICE": 0.030},
    "Heavy Duty": {"EV": 0.035, "ICE": 0.042},
}

# Insurance as % of MSRP in Year 1; declines 3% per year after
INSURANCE_PCT_OF_MSRP_YEAR1 = 0.025
INSURANCE_ANNUAL_DECLINE = 0.03

# Salvage value as % of MSRP at end of analysis period
SALVAGE_PCT = {
    "EV": 0.15,
    "ICE": 0.20,
}

# Annual charger maintenance as % of charger capex
CHARGER_MAINTENANCE_PCT = 0.02

# Carbon intensity assumptions for carbon credit calculations (tCO2e/km)
ICE_CO2_TONNE_PER_KM = {
    "Diesel": 0.000267,
    "Gasoline": 0.000233,
    "Propane": 0.000215,
}
EV_CO2_TONNE_PER_KM = 0.000020  # Grid-average assumption

# Default fallback electricity rate if province not found
DEFAULT_ELECTRICITY_RATE = 0.13  # $/kWh
DEFAULT_GASOLINE_PRICE = 1.65    # $/L
DEFAULT_DIESEL_PRICE = 1.70      # $/L

# Default maintenance cost per km if DB lookup fails
DEFAULT_MAINTENANCE_COST_PER_KM = {
    "EV": 0.043,
    "ICE": 0.063,
}

# iMHZEV purchase year cap
IMHZEV_PURCHASE_YEAR_CAP = 3

PROVINCES = ["ON", "BC", "AB", "SK", "MB", "QC", "NB", "NS", "PEI", "NL", "NT", "YT", "NU"]

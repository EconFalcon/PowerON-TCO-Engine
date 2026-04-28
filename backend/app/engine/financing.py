"""
PMT and lease payment calculations mirroring Excel formulas.
"""


def pmt(annual_rate: float, term_months: int, principal: float) -> float:
    """Standard Excel PMT formula: monthly payment on a loan."""
    if principal <= 0:
        return 0.0
    r = annual_rate / 12
    if r == 0:
        return principal / term_months
    return r * principal / (1 - (1 + r) ** -term_months)


def annual_loan_payment(annual_rate: float, term_months: int, principal: float) -> float:
    """Total annual payment = PMT * 12 (or fewer months in final partial year)."""
    return pmt(annual_rate, term_months, principal) * 12


def monthly_lease_payment(msrp: float, residual_pct: float, money_factor: float, term_months: int) -> float:
    """Standard money-factor lease payment formula."""
    residual = msrp * residual_pct
    depreciation = (msrp - residual) / term_months
    finance_charge = (msrp + residual) * money_factor
    return depreciation + finance_charge


def vehicle_cost_by_year(
    scenario_id: int,
    msrp: float,
    charger_capex: float,
    loan_rate: float,
    loan_down_pct: float,
    loan_term_months: int,
    money_factor: float,
    lease_term_months: int,
    lease_residual_pct: float,
    year: int,  # 1-indexed, year 1 = first operating year
    fleet_size: int,
) -> tuple[float, float]:
    """
    Returns (vehicle_cost_per_fleet, charger_cost) for a given year and scenario.

    Scenario 1 - Cash: full vehicle cost in year 1, charger cost in year 1
    Scenario 2 - Hybrid Finance: vehicle financed (loan), charger cash in year 1
    Scenario 3 - Full Finance: vehicle + charger both financed (separate loans)
    Scenario 4 - Lease: vehicle leased, charger cash in year 1
    """
    total_msrp = msrp * fleet_size
    loan_principal = total_msrp * (1 - loan_down_pct)
    down_payment = total_msrp * loan_down_pct
    loan_years = loan_term_months / 12

    if scenario_id == 1:  # Cash
        veh_cost = total_msrp if year == 1 else 0.0
        chrg_cost = charger_capex if year == 1 else 0.0

    elif scenario_id == 2:  # Hybrid Finance (vehicle financed, charger cash)
        if year == 1:
            veh_cost = down_payment + annual_loan_payment(loan_rate, loan_term_months, loan_principal)
        elif 1 < year <= loan_years:
            veh_cost = annual_loan_payment(loan_rate, loan_term_months, loan_principal)
        else:
            veh_cost = 0.0
        chrg_cost = charger_capex if year == 1 else 0.0

    elif scenario_id == 3:  # Full Finance
        if year == 1:
            veh_cost = down_payment + annual_loan_payment(loan_rate, loan_term_months, loan_principal)
        elif 1 < year <= loan_years:
            veh_cost = annual_loan_payment(loan_rate, loan_term_months, loan_principal)
        else:
            veh_cost = 0.0
        # Charger also financed (assume same loan terms, no down payment)
        charger_loan_years = loan_term_months / 12
        if year <= charger_loan_years:
            chrg_cost = annual_loan_payment(loan_rate, loan_term_months, charger_capex)
        else:
            chrg_cost = 0.0

    elif scenario_id == 4:  # Lease
        monthly_pmt = monthly_lease_payment(msrp, lease_residual_pct, money_factor, lease_term_months)
        lease_years = lease_term_months / 12
        if year <= lease_years:
            veh_cost = monthly_pmt * 12 * fleet_size
        else:
            veh_cost = 0.0
        chrg_cost = charger_capex if year == 1 else 0.0

    else:
        raise ValueError(f"Unknown scenario_id: {scenario_id}")

    return veh_cost, chrg_cost

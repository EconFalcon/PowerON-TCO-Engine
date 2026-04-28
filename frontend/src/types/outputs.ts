export interface YearCostBreakdown {
  year: number;
  vehicle_cost: number;
  fuel_or_electricity: number;
  maintenance: number;
  tires: number;
  insurance: number;
  charger_cost: number;
  rebates: number;
  salvage: number;
  total: number;
}

export interface VehicleSummary {
  id: number;
  display_name: string;
  msrp_cad: number;
  category: string;
}

export interface ScenarioTCO {
  scenario_name: string;
  scenario_id: number;
  ev_total_tco: number;
  ice_total_tco: number;
  ev_npv: number;
  ice_npv: number;
  ev_cost_per_km: number;
  ice_cost_per_km: number;
  savings_vs_ice: number;
  break_even_year: number | null;
  ev_yearly: YearCostBreakdown[];
  ice_yearly: YearCostBreakdown[];
}

export interface TCOResult {
  scenarios: ScenarioTCO[];
  recommended_ev: VehicleSummary;
  recommended_ice: VehicleSummary;
  charger_count: number;
  charger_total_cost: number;
  calculation_timestamp: string;
}

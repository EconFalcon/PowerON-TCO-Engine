export interface EVVehicle {
  id: number;
  display_name: string;
  make: string;
  model: string;
  year: number | null;
  msrp_cad: number;
  battery_kwh: number;
  efficiency_kwh_per_km: number;
  range_km: number;
  payload_lbs: number;
  category: string;
  has_refrigeration: boolean;
}

export interface ICEVehicle {
  id: number;
  display_name: string;
  make: string;
  model: string;
  year: number | null;
  msrp_cad: number;
  fuel_type: string;
  fuel_consumption_l_per_100km: number;
  payload_lbs: number;
  category: string;
}

export interface Charger {
  id: number;
  display_name: string;
  type_name: string;
  power_kw: number;
  unit_cost_cad: number;
  installation_cost_cad: number;
  lifespan_years: number;
}

export interface SavedScenario {
  id: number;
  name: string;
  created_at: string;
  province: string;
  ev_fleet_size: number;
  ice_fleet_size: number;
  vehicle_category: string;
  ev_total_tco_cash: number | null;
}

export interface DutyCycle {
  daily_distance_km: number;
  max_payload_lbs: number;
  vehicle_category: string;
  refrigeration_required: boolean;
}

export interface FleetParams {
  province: string;
  ev_fleet_size: number;
  ice_fleet_size: number;
  annual_km_per_vehicle: number;
  depot_charging_pct: number;
  public_charging_rate_per_kwh: number;
  ev_vehicles_per_charger: number;
}

export interface VehicleSelection {
  ev_model_id: number | null;
  ice_model_id: number | null;
  charger_type_id: number | null;
}

export interface LoanParams {
  interest_rate: number;
  down_payment_pct: number;
  loan_term_months: number;
}

export interface LeaseParams {
  money_factor: number;
  lease_term_months: number;
  residual_value_pct: number;
}

export interface TCOInputs {
  duty_cycle: DutyCycle;
  fleet: FleetParams;
  vehicles: VehicleSelection;
  loan: LoanParams;
  lease: LeaseParams;
  analysis_year: number;
  discount_rate: number;
}

export const DEFAULT_INPUTS: TCOInputs = {
  duty_cycle: {
    daily_distance_km: 300,
    max_payload_lbs: 1500,
    vehicle_category: 'Light Duty',
    refrigeration_required: false,
  },
  fleet: {
    province: 'ON',
    ev_fleet_size: 5,
    ice_fleet_size: 5,
    annual_km_per_vehicle: 40000,
    depot_charging_pct: 0.8,
    public_charging_rate_per_kwh: 0.465,
    ev_vehicles_per_charger: 1,
  },
  vehicles: {
    ev_model_id: null,
    ice_model_id: null,
    charger_type_id: null,
  },
  loan: {
    interest_rate: 0.065,
    down_payment_pct: 0.20,
    loan_term_months: 60,
  },
  lease: {
    money_factor: 0.00125,
    lease_term_months: 48,
    residual_value_pct: 0.50,
  },
  analysis_year: 2025,
  discount_rate: 0.08,
};

export const VEHICLE_CATEGORIES = ['Light Duty', 'Medium Duty', 'Heavy Duty'];
export const PROVINCES = ['ON', 'BC', 'AB', 'QC', 'SK', 'MB', 'NB', 'NS', 'PEI', 'NL', 'YT', 'NT', 'NU'];

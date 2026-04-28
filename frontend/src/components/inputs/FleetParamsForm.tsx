import { useInputStore } from '../../store/useInputStore';
import { LabeledField, Input, Select, SectionTitle } from '../common';
import { PROVINCES } from '../../types/inputs';

export default function FleetParamsForm() {
  const { fleet, setFleet } = useInputStore();

  return (
    <div>
      <SectionTitle>Fleet Parameters</SectionTitle>

      <LabeledField label="Province">
        <Select value={fleet.province} onChange={(e) => setFleet({ province: e.target.value })}>
          {PROVINCES.map((p) => <option key={p} value={p}>{p}</option>)}
        </Select>
      </LabeledField>

      <div className="grid grid-cols-2 gap-3">
        <LabeledField label="EV Fleet Size" hint="vehicles">
          <Input type="number" min={1} value={fleet.ev_fleet_size}
            onChange={(e) => setFleet({ ev_fleet_size: +e.target.value })} />
        </LabeledField>
        <LabeledField label="ICE Fleet Size" hint="vehicles">
          <Input type="number" min={1} value={fleet.ice_fleet_size}
            onChange={(e) => setFleet({ ice_fleet_size: +e.target.value })} />
        </LabeledField>
      </div>

      <LabeledField label="Annual KM per Vehicle">
        <Input type="number" min={1} value={fleet.annual_km_per_vehicle}
          onChange={(e) => setFleet({ annual_km_per_vehicle: +e.target.value })} />
      </LabeledField>

      <LabeledField label="Depot Charging %" hint="0–100">
        <Input type="number" min={0} max={100} value={fleet.depot_charging_pct * 100}
          onChange={(e) => setFleet({ depot_charging_pct: +e.target.value / 100 })} />
      </LabeledField>

      <LabeledField label="Public Charging Rate" hint="$/kWh">
        <Input type="number" min={0} step={0.01} value={fleet.public_charging_rate_per_kwh}
          onChange={(e) => setFleet({ public_charging_rate_per_kwh: +e.target.value })} />
      </LabeledField>

      <LabeledField label="EVs per Charger">
        <Input type="number" min={0.1} step={0.1} value={fleet.ev_vehicles_per_charger}
          onChange={(e) => setFleet({ ev_vehicles_per_charger: +e.target.value })} />
      </LabeledField>
    </div>
  );
}

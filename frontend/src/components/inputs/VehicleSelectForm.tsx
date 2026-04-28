import { useEffect } from 'react';
import { useInputStore } from '../../store/useInputStore';
import { useReferenceStore } from '../../store/useReferenceStore';
import { LabeledField, Select, SectionTitle, LoadingSpinner } from '../common';
import { formatCurrency } from '../../utils/formatters';

export default function VehicleSelectForm() {
  const { vehicles, setVehicles, duty_cycle } = useInputStore();
  const { evVehicles, iceVehicles, chargers, isLoaded, load } = useReferenceStore();

  useEffect(() => { load(); }, [load]);

  const filteredEV = evVehicles.filter(
    (v) => !duty_cycle.vehicle_category || v.category === duty_cycle.vehicle_category
  );
  const filteredICE = iceVehicles.filter(
    (v) => !duty_cycle.vehicle_category || v.category === duty_cycle.vehicle_category
  );

  if (!isLoaded) return <LoadingSpinner />;

  return (
    <div>
      <SectionTitle>Vehicle & Charger Selection</SectionTitle>

      <LabeledField label="EV Model">
        <Select
          value={vehicles.ev_model_id ?? ''}
          onChange={(e) => setVehicles({ ev_model_id: e.target.value ? +e.target.value : null })}
        >
          <option value="">Auto-select (best match)</option>
          {filteredEV.map((v) => (
            <option key={v.id} value={v.id}>
              {v.display_name} — {formatCurrency(v.msrp_cad)} | {v.range_km.toFixed(0)} km range
            </option>
          ))}
        </Select>
      </LabeledField>

      <LabeledField label="ICE Model">
        <Select
          value={vehicles.ice_model_id ?? ''}
          onChange={(e) => setVehicles({ ice_model_id: e.target.value ? +e.target.value : null })}
        >
          <option value="">Auto-select (best match)</option>
          {filteredICE.map((v) => (
            <option key={v.id} value={v.id}>
              {v.display_name} — {formatCurrency(v.msrp_cad)} | {v.fuel_type}
            </option>
          ))}
        </Select>
      </LabeledField>

      <LabeledField label="Charger Type">
        <Select
          value={vehicles.charger_type_id ?? ''}
          onChange={(e) => setVehicles({ charger_type_id: e.target.value ? +e.target.value : null })}
        >
          <option value="">Auto-select (lowest cost)</option>
          {chargers.map((c) => (
            <option key={c.id} value={c.id}>
              {c.display_name} — {formatCurrency(c.unit_cost_cad + c.installation_cost_cad)} total
            </option>
          ))}
        </Select>
      </LabeledField>
    </div>
  );
}

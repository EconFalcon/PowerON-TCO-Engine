import { useInputStore } from '../../store/useInputStore';
import { LabeledField, Input, Select, Toggle, SectionTitle } from '../common';
import { VEHICLE_CATEGORIES } from '../../types/inputs';

export default function DutyCycleForm() {
  const { duty_cycle, setDutyCycle } = useInputStore();

  return (
    <div>
      <SectionTitle>Duty Cycle Requirements</SectionTitle>

      <LabeledField label="Required Daily Distance" hint="km">
        <Input
          type="number"
          min={1}
          value={duty_cycle.daily_distance_km}
          onChange={(e) => setDutyCycle({ daily_distance_km: +e.target.value })}
        />
      </LabeledField>

      <LabeledField label="Maximum Payload" hint="lbs">
        <Input
          type="number"
          min={0}
          value={duty_cycle.max_payload_lbs}
          onChange={(e) => setDutyCycle({ max_payload_lbs: +e.target.value })}
        />
      </LabeledField>

      <LabeledField label="Vehicle Category">
        <Select
          value={duty_cycle.vehicle_category}
          onChange={(e) => setDutyCycle({ vehicle_category: e.target.value })}
        >
          {VEHICLE_CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </Select>
      </LabeledField>

      <LabeledField label="Refrigeration Required">
        <Toggle
          checked={duty_cycle.refrigeration_required}
          onChange={(v) => setDutyCycle({ refrigeration_required: v })}
          label={duty_cycle.refrigeration_required ? 'Yes' : 'No'}
        />
      </LabeledField>
    </div>
  );
}

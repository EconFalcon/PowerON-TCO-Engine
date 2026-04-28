import { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { TCOResult } from '../../types/outputs';
import { COST_COMPONENT_COLORS } from '../../utils/chartColors';
import { formatCurrencyCompact } from '../../utils/formatters';

const COMPONENTS = [
  { key: 'vehicle_cost', label: 'Vehicle' },
  { key: 'fuel_or_electricity', label: 'Energy' },
  { key: 'maintenance', label: 'Maintenance' },
  { key: 'charger_cost', label: 'Charger' },
  { key: 'insurance', label: 'Insurance' },
  { key: 'tires', label: 'Tires' },
];

export default function AnnualCostBreakdownChart({ result }: { result: TCOResult }) {
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const scenario = result.scenarios[scenarioIdx];

  const data = scenario.ev_yearly.map((y) => ({
    year: y.year,
    Vehicle: y.vehicle_cost,
    Energy: y.fuel_or_electricity,
    Maintenance: y.maintenance,
    Charger: y.charger_cost,
    Insurance: y.insurance,
    Tires: y.tires,
    Rebates: -y.rebates,
  }));

  return (
    <div>
      <div className="flex gap-2 mb-2">
        {result.scenarios.map((s, i) => (
          <button key={s.scenario_id} onClick={() => setScenarioIdx(i)}
            className={`px-2 py-0.5 text-xs rounded border ${scenarioIdx === i ? 'bg-green-700 text-white border-green-700' : 'text-gray-600 border-gray-300'}`}>
            {s.scenario_name}
          </button>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="year" tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={(v) => formatCurrencyCompact(v)} tick={{ fontSize: 10 }} width={65} />
          <Tooltip formatter={(v: any) => [formatCurrencyCompact(Math.abs(v as number))]} />
          <Legend iconSize={10} wrapperStyle={{ fontSize: 10 }} />
          {COMPONENTS.map((c) => (
            <Bar key={c.key} dataKey={c.label} stackId="a" fill={COST_COMPONENT_COLORS[c.key]} />
          ))}
          <Bar dataKey="Rebates" stackId="a" fill={COST_COMPONENT_COLORS.rebates} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

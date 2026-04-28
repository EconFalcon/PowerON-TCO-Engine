import { TCOResult } from '../../types/outputs';
import { formatCurrency, formatKm } from '../../utils/formatters';

export default function ScenarioCompTable({ result }: { result: TCOResult }) {
  const rows = [
    { label: 'EV Total TCO', fn: (s: any) => formatCurrency(s.ev_total_tco) },
    { label: 'ICE Total TCO', fn: (s: any) => formatCurrency(s.ice_total_tco) },
    { label: 'EV NPV', fn: (s: any) => formatCurrency(s.ev_npv) },
    { label: 'ICE NPV', fn: (s: any) => formatCurrency(s.ice_npv) },
    { label: 'EV Cost/km', fn: (s: any) => formatKm(s.ev_cost_per_km) },
    { label: 'ICE Cost/km', fn: (s: any) => formatKm(s.ice_cost_per_km) },
    { label: '10-yr Savings', fn: (s: any) => formatCurrency(s.savings_vs_ice) },
    { label: 'Break-even', fn: (s: any) => s.break_even_year ? `Year ${s.break_even_year}` : '>10 yrs' },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-green-800 text-white">
            <th className="px-3 py-2 text-left font-semibold">Metric</th>
            {result.scenarios.map((s) => (
              <th key={s.scenario_id} className="px-3 py-2 text-center font-semibold">{s.scenario_name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={row.label} className={i % 2 === 0 ? 'bg-green-50' : 'bg-white'}>
              <td className="px-3 py-2 font-medium text-gray-600">{row.label}</td>
              {result.scenarios.map((s) => (
                <td key={s.scenario_id} className="px-3 py-2 text-center text-gray-800">{row.fn(s)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

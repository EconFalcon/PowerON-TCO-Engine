import { useState } from 'react';
import { TCOResult } from '../../types/outputs';
import { formatCurrency } from '../../utils/formatters';

export default function YearlyBreakdownTable({ result }: { result: TCOResult }) {
  const [selected, setSelected] = useState(0);
  const scenario = result.scenarios[selected];

  return (
    <div>
      <div className="flex gap-2 mb-3">
        {result.scenarios.map((s, i) => (
          <button
            key={s.scenario_id}
            onClick={() => setSelected(i)}
            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
              selected === i ? 'bg-green-700 text-white border-green-700' : 'bg-white text-gray-600 border-gray-300 hover:border-green-500'
            }`}
          >
            {s.scenario_name}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto text-xs">
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-100 text-gray-600">
              <th className="px-2 py-1.5 text-left">Yr</th>
              <th className="px-2 py-1.5 text-right">Vehicle</th>
              <th className="px-2 py-1.5 text-right">Energy</th>
              <th className="px-2 py-1.5 text-right">Maint.</th>
              <th className="px-2 py-1.5 text-right">Charger</th>
              <th className="px-2 py-1.5 text-right">Insur.</th>
              <th className="px-2 py-1.5 text-right">Rebates</th>
              <th className="px-2 py-1.5 text-right font-semibold">EV Total</th>
              <th className="px-2 py-1.5 text-right font-semibold">ICE Total</th>
            </tr>
          </thead>
          <tbody>
            {scenario.ev_yearly.map((ev, i) => {
              const ice = scenario.ice_yearly[i];
              return (
                <tr key={ev.year} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-2 py-1.5 text-gray-500">{ev.year}</td>
                  <td className="px-2 py-1.5 text-right">{formatCurrency(ev.vehicle_cost)}</td>
                  <td className="px-2 py-1.5 text-right">{formatCurrency(ev.fuel_or_electricity)}</td>
                  <td className="px-2 py-1.5 text-right">{formatCurrency(ev.maintenance)}</td>
                  <td className="px-2 py-1.5 text-right">{formatCurrency(ev.charger_cost)}</td>
                  <td className="px-2 py-1.5 text-right">{formatCurrency(ev.insurance)}</td>
                  <td className="px-2 py-1.5 text-right text-red-600">-{formatCurrency(ev.rebates)}</td>
                  <td className="px-2 py-1.5 text-right font-semibold text-green-700">{formatCurrency(ev.total)}</td>
                  <td className="px-2 py-1.5 text-right font-semibold text-red-700">{formatCurrency(ice.total)}</td>
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr className="bg-green-800 text-white font-bold">
              <td className="px-2 py-1.5">Total</td>
              <td colSpan={6} />
              <td className="px-2 py-1.5 text-right">{formatCurrency(scenario.ev_total_tco)}</td>
              <td className="px-2 py-1.5 text-right">{formatCurrency(scenario.ice_total_tco)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}

import { TCOResult } from '../../types/outputs';
import { formatCurrency, formatKm } from '../../utils/formatters';

export default function SummaryCards({ result }: { result: TCOResult }) {
  const cash = result.scenarios[0];

  const cards = [
    { label: 'EV Fleet (Cash)', value: formatCurrency(cash.ev_total_tco), sub: '10-year total', color: 'green' },
    { label: 'ICE Fleet (Cash)', value: formatCurrency(cash.ice_total_tco), sub: '10-year total', color: 'red' },
    { label: 'Total Savings', value: formatCurrency(cash.savings_vs_ice), sub: 'EV vs ICE (Cash)', color: 'blue' },
    { label: 'Break-even', value: cash.break_even_year ? `Year ${cash.break_even_year}` : '>10 yrs', sub: 'EV cheaper than ICE', color: 'purple' },
    { label: 'EV Cost/km', value: formatKm(cash.ev_cost_per_km), sub: '10-yr average', color: 'green' },
    { label: 'ICE Cost/km', value: formatKm(cash.ice_cost_per_km), sub: '10-yr average', color: 'red' },
  ];

  const colors: Record<string, string> = {
    green: 'border-green-500 bg-green-50',
    red: 'border-red-500 bg-red-50',
    blue: 'border-blue-500 bg-blue-50',
    purple: 'border-purple-500 bg-purple-50',
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
      {cards.map((c) => (
        <div key={c.label} className={`rounded-lg border-l-4 p-3 ${colors[c.color]}`}>
          <div className="text-xs text-gray-500 mb-1">{c.label}</div>
          <div className="text-lg font-bold text-gray-800">{c.value}</div>
          <div className="text-xs text-gray-400">{c.sub}</div>
        </div>
      ))}
    </div>
  );
}

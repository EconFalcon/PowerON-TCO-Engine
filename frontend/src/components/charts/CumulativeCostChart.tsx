import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { TCOResult } from '../../types/outputs';
import { SCENARIO_COLORS } from '../../utils/chartColors';
import { formatCurrencyCompact } from '../../utils/formatters';

export default function CumulativeCostChart({ result }: { result: TCOResult }) {
  // Build cumulative data points
  const data = result.scenarios[0].ev_yearly.map((_, i) => {
    const point: Record<string, number | string> = { year: i + 1 };
    result.scenarios.forEach((s) => {
      const evCum = s.ev_yearly.slice(0, i + 1).reduce((acc, y) => acc + y.total, 0);
      const iceCum = s.ice_yearly.slice(0, i + 1).reduce((acc, y) => acc + y.total, 0);
      point[`ev_${s.scenario_id}`] = evCum;
      point[`ice_${s.scenario_id}`] = iceCum;
    });
    return point;
  });

  const DASH = ['', '5 5', '8 3', '3 3'];

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="year" label={{ value: 'Year', position: 'insideBottom', offset: -2 }} tick={{ fontSize: 11 }} />
        <YAxis tickFormatter={(v) => formatCurrencyCompact(v)} tick={{ fontSize: 10 }} width={70} />
        <Tooltip
          formatter={(v: any) => [formatCurrencyCompact(v as number)]}
          labelFormatter={(l: any) => `Year ${l}`}
        />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 10 }} />
        {result.scenarios.map((s, i) => (
          <>
            <Line
              key={`ev_${s.scenario_id}`}
              dataKey={`ev_${s.scenario_id}`}
              name={`EV – ${s.scenario_name}`}
              stroke={SCENARIO_COLORS[i]}
              strokeWidth={2}
              dot={false}
            />
            <Line
              key={`ice_${s.scenario_id}`}
              dataKey={`ice_${s.scenario_id}`}
              name={`ICE – ${s.scenario_name}`}
              stroke={SCENARIO_COLORS[i]}
              strokeWidth={1.5}
              strokeDasharray={DASH[i] || '5 5'}
              dot={false}
              opacity={0.7}
            />
          </>
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

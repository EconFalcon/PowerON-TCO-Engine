import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { TCOResult } from '../../types/outputs';
import { EV_COLOR, ICE_COLOR } from '../../utils/chartColors';
import { formatCurrencyCompact } from '../../utils/formatters';

export default function ScenarioCompBarChart({ result }: { result: TCOResult }) {
  const data = result.scenarios.map((s) => ({
    name: s.scenario_name,
    'EV Fleet': s.ev_total_tco,
    'ICE Fleet': s.ice_total_tco,
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 15, right: 10, bottom: 5, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
        <YAxis tickFormatter={(v) => formatCurrencyCompact(v)} tick={{ fontSize: 10 }} width={65} />
        <Tooltip formatter={(v: any) => [formatCurrencyCompact(v as number)]} />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="EV Fleet" fill={EV_COLOR} radius={[3, 3, 0, 0]} label={{ position: 'top', formatter: (v: any) => formatCurrencyCompact(v as number), fontSize: 9 }} />
        <Bar dataKey="ICE Fleet" fill={ICE_COLOR} radius={[3, 3, 0, 0]} label={{ position: 'top', formatter: (v: any) => formatCurrencyCompact(v as number), fontSize: 9 }} />
      </BarChart>
    </ResponsiveContainer>
  );
}

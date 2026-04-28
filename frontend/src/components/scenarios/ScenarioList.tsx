import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { deleteScenario, fetchScenario } from '../../api/scenarios';
import { useScenarioStore } from '../../store/useScenarioStore';
import { useInputStore } from '../../store/useInputStore';
import { useResultStore } from '../../store/useResultStore';
import { Button, LoadingSpinner } from '../common';
import { formatCurrency } from '../../utils/formatters';

export default function ScenarioList() {
  const { scenarios, isLoading, load, remove } = useScenarioStore();
  const { loadInputs } = useInputStore();
  const { setResult } = useResultStore();
  const navigate = useNavigate();

  useEffect(() => { load(); }, [load]);

  async function handleLoad(id: number) {
    const detail = await fetchScenario(id);
    loadInputs(detail.inputs);
    if (detail.result) setResult(detail.result);
    navigate('/');
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this scenario?')) return;
    await deleteScenario(id);
    remove(id);
  }

  if (isLoading) return <LoadingSpinner />;
  if (scenarios.length === 0) {
    return <div className="text-center text-gray-400 py-12">No saved scenarios yet. Calculate and save one from the calculator.</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-green-800 text-white text-left">
            <th className="px-4 py-2 font-semibold">Name</th>
            <th className="px-4 py-2 font-semibold">Province</th>
            <th className="px-4 py-2 font-semibold">Category</th>
            <th className="px-4 py-2 font-semibold">EV Fleet</th>
            <th className="px-4 py-2 font-semibold">EV TCO (Cash)</th>
            <th className="px-4 py-2 font-semibold">Date</th>
            <th className="px-4 py-2" />
          </tr>
        </thead>
        <tbody>
          {scenarios.map((s, i) => (
            <tr key={s.id} className={i % 2 === 0 ? 'bg-white hover:bg-green-50' : 'bg-gray-50 hover:bg-green-50'}>
              <td className="px-4 py-2 font-medium">{s.name}</td>
              <td className="px-4 py-2">{s.province}</td>
              <td className="px-4 py-2">{s.vehicle_category}</td>
              <td className="px-4 py-2">{s.ev_fleet_size} vehicles</td>
              <td className="px-4 py-2">{s.ev_total_tco_cash != null ? formatCurrency(s.ev_total_tco_cash) : '—'}</td>
              <td className="px-4 py-2 text-gray-400 text-xs">{new Date(s.created_at).toLocaleDateString()}</td>
              <td className="px-4 py-2 flex gap-2">
                <Button size="sm" onClick={() => handleLoad(s.id)}>Load</Button>
                <Button size="sm" variant="danger" onClick={() => handleDelete(s.id)}>Delete</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

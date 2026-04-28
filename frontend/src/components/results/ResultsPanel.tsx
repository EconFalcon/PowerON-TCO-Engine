import { useResultStore } from '../../store/useResultStore';
import { LoadingSpinner, ErrorBanner, Card } from '../common';
import SummaryCards from './SummaryCards';
import ScenarioCompTable from './ScenarioCompTable';
import YearlyBreakdownTable from './YearlyBreakdownTable';
import CumulativeCostChart from '../charts/CumulativeCostChart';
import AnnualCostBreakdownChart from '../charts/AnnualCostBreakdownChart';
import ScenarioCompBarChart from '../charts/ScenarioCompBarChart';
import { formatCurrency } from '../../utils/formatters';

export default function ResultsPanel() {
  const { result, isLoading, error } = useResultStore();

  if (isLoading) return <div className="p-8"><LoadingSpinner /></div>;
  if (error) return <div className="p-8"><ErrorBanner message={error} /></div>;

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400 p-12">
        <div className="text-5xl mb-4">⚡</div>
        <p className="text-lg font-medium text-gray-500">Enter your fleet parameters and click Calculate TCO</p>
        <p className="text-sm mt-2">Compare EV vs ICE costs across 4 financing scenarios</p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4 overflow-y-auto">
      {/* Vehicle recommendation strip */}
      <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-3 flex flex-wrap gap-6 text-sm">
        <span><span className="text-gray-500">Recommended EV:</span> <strong className="text-green-800">{result.recommended_ev.display_name}</strong> — {formatCurrency(result.recommended_ev.msrp_cad)}</span>
        <span><span className="text-gray-500">Recommended ICE:</span> <strong className="text-gray-700">{result.recommended_ice.display_name}</strong> — {formatCurrency(result.recommended_ice.msrp_cad)}</span>
        <span><span className="text-gray-500">Chargers needed:</span> <strong>{result.charger_count}</strong> ({formatCurrency(result.charger_total_cost)} capex)</span>
      </div>

      <SummaryCards result={result} />

      <Card className="p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Scenario Comparison</h3>
        <ScenarioCompTable result={result} />
      </Card>

      <Card className="p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">10-Year Cumulative Cost</h3>
        <CumulativeCostChart result={result} />
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <Card className="p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Annual Cost Breakdown (EV)</h3>
          <AnnualCostBreakdownChart result={result} />
        </Card>
        <Card className="p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">TCO by Scenario</h3>
          <ScenarioCompBarChart result={result} />
        </Card>
      </div>

      <Card className="p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Year-by-Year Cost Detail</h3>
        <YearlyBreakdownTable result={result} />
      </Card>
    </div>
  );
}

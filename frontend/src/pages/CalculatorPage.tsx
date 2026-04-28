import InputPanel from '../components/inputs/InputPanel';
import ResultsPanel from '../components/results/ResultsPanel';

export default function CalculatorPage() {
  return (
    <div className="flex h-screen">
      {/* Input panel — fixed 380px */}
      <div className="w-96 border-r border-gray-200 bg-white flex flex-col shrink-0">
        <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
          <h1 className="text-base font-semibold text-gray-800">Fleet TCO Calculator</h1>
          <p className="text-xs text-gray-500 mt-0.5">10-year EV vs ICE total cost comparison</p>
        </div>
        <div className="flex-1 overflow-hidden flex flex-col">
          <InputPanel />
        </div>
      </div>

      {/* Results panel — fills remaining space */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        <ResultsPanel />
      </div>
    </div>
  );
}

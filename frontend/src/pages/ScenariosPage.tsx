import ScenarioList from '../components/scenarios/ScenarioList';

export default function ScenariosPage() {
  return (
    <div className="p-6">
      <div className="mb-5">
        <h1 className="text-xl font-semibold text-gray-800">Saved Scenarios</h1>
        <p className="text-sm text-gray-500 mt-1">Load a saved scenario to continue working on it or compare results.</p>
      </div>
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <ScenarioList />
      </div>
    </div>
  );
}

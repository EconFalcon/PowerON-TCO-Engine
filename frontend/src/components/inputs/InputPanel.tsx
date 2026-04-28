import { useState } from 'react';
import { calculateTCO } from '../../api/calculate';
import { exportPDF } from '../../api/export';
import { useInputStore } from '../../store/useInputStore';
import { useResultStore } from '../../store/useResultStore';
import { Button } from '../common';
import DutyCycleForm from './DutyCycleForm';
import FleetParamsForm from './FleetParamsForm';
import VehicleSelectForm from './VehicleSelectForm';
import FinancingForm from './FinancingForm';
import SaveScenarioModal from '../scenarios/SaveScenarioModal';

const TABS = ['Duty Cycle', 'Fleet', 'Vehicles', 'Financing'];

export default function InputPanel() {
  const [activeTab, setActiveTab] = useState(0);
  const [showSave, setShowSave] = useState(false);
  const [exporting, setExporting] = useState(false);
  const { getInputs } = useInputStore();
  const { setResult, setLoading, setError, isLoading, result } = useResultStore();

  async function handleCalculate() {
    setLoading(true);
    setError(null);
    try {
      const res = await calculateTCO(getInputs());
      setResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Calculation failed. Check your inputs.');
    }
  }

  async function handleExport() {
    setExporting(true);
    try {
      await exportPDF(getInputs());
    } catch {
      alert('PDF export failed.');
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-white">
        {TABS.map((tab, i) => (
          <button
            key={tab}
            onClick={() => setActiveTab(i)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === i
                ? 'border-green-600 text-green-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Form content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 0 && <DutyCycleForm />}
        {activeTab === 1 && <FleetParamsForm />}
        {activeTab === 2 && <VehicleSelectForm />}
        {activeTab === 3 && <FinancingForm />}
      </div>

      {/* Action buttons */}
      <div className="border-t border-gray-200 bg-white p-4 flex gap-2 flex-wrap">
        <Button onClick={handleCalculate} disabled={isLoading} size="lg" className="flex-1">
          {isLoading ? 'Calculating...' : 'Calculate TCO'}
        </Button>
        <Button variant="secondary" onClick={() => setShowSave(true)} disabled={!result} size="lg">
          Save
        </Button>
        <Button variant="secondary" onClick={handleExport} disabled={!result || exporting} size="lg">
          {exporting ? 'Exporting...' : 'PDF'}
        </Button>
      </div>

      {showSave && <SaveScenarioModal onClose={() => setShowSave(false)} />}
    </div>
  );
}

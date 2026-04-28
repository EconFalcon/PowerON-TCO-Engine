import { useState } from 'react';
import { saveScenario } from '../../api/scenarios';
import { useInputStore } from '../../store/useInputStore';
import { useScenarioStore } from '../../store/useScenarioStore';
import { Button, Input } from '../common';

export default function SaveScenarioModal({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState('');
  const { getInputs } = useInputStore();
  const { add } = useScenarioStore();

  async function handleSave() {
    if (!name.trim()) { setErr('Please enter a name'); return; }
    setSaving(true);
    try {
      await saveScenario(name.trim(), getInputs());
      onClose();
    } catch {
      setErr('Failed to save. Please try again.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl p-6 w-80">
        <h2 className="text-base font-semibold text-gray-800 mb-4">Save Scenario</h2>
        <Input
          placeholder="Scenario name (e.g. ON Fleet Q2 2025)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSave()}
          autoFocus
        />
        {err && <p className="text-red-600 text-xs mt-1">{err}</p>}
        <div className="flex gap-2 mt-4">
          <Button onClick={handleSave} disabled={saving} className="flex-1">{saving ? 'Saving...' : 'Save'}</Button>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
        </div>
      </div>
    </div>
  );
}

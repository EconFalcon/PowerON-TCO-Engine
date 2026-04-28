import { create } from 'zustand';
import { SavedScenario } from '../types/reference';
import { fetchScenarios } from '../api/scenarios';

interface ScenarioState {
  scenarios: SavedScenario[];
  isLoading: boolean;
  load: () => Promise<void>;
  remove: (id: number) => void;
  add: (s: SavedScenario) => void;
}

export const useScenarioStore = create<ScenarioState>((set) => ({
  scenarios: [],
  isLoading: false,
  load: async () => {
    set({ isLoading: true });
    const data = await fetchScenarios();
    set({ scenarios: data, isLoading: false });
  },
  remove: (id) => set((s) => ({ scenarios: s.scenarios.filter((x) => x.id !== id) })),
  add: (scenario) => set((s) => ({ scenarios: [scenario as SavedScenario, ...s.scenarios] })),
}));

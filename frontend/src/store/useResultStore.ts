import { create } from 'zustand';
import { TCOResult } from '../types/outputs';

interface ResultState {
  result: TCOResult | null;
  isLoading: boolean;
  error: string | null;
  setResult: (r: TCOResult) => void;
  setLoading: (b: boolean) => void;
  setError: (e: string | null) => void;
  clear: () => void;
}

export const useResultStore = create<ResultState>((set) => ({
  result: null,
  isLoading: false,
  error: null,
  setResult: (r) => set({ result: r, error: null, isLoading: false }),
  setLoading: (b) => set({ isLoading: b }),
  setError: (e) => set({ error: e, isLoading: false }),
  clear: () => set({ result: null, error: null }),
}));

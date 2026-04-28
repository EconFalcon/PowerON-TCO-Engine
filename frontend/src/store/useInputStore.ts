import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { TCOInputs, DutyCycle, FleetParams, VehicleSelection, LoanParams, LeaseParams, DEFAULT_INPUTS } from '../types/inputs';

interface InputState extends TCOInputs {
  setDutyCycle: (v: Partial<DutyCycle>) => void;
  setFleet: (v: Partial<FleetParams>) => void;
  setVehicles: (v: Partial<VehicleSelection>) => void;
  setLoan: (v: Partial<LoanParams>) => void;
  setLease: (v: Partial<LeaseParams>) => void;
  setField: (section: keyof TCOInputs, key: string, val: unknown) => void;
  loadInputs: (inputs: TCOInputs) => void;
  reset: () => void;
  getInputs: () => TCOInputs;
}

export const useInputStore = create<InputState>()(
  persist(
    (set, get) => ({
      ...DEFAULT_INPUTS,
      setDutyCycle: (v) => set((s) => ({ duty_cycle: { ...s.duty_cycle, ...v } })),
      setFleet: (v) => set((s) => ({ fleet: { ...s.fleet, ...v } })),
      setVehicles: (v) => set((s) => ({ vehicles: { ...s.vehicles, ...v } })),
      setLoan: (v) => set((s) => ({ loan: { ...s.loan, ...v } })),
      setLease: (v) => set((s) => ({ lease: { ...s.lease, ...v } })),
      setField: (section, key, val) =>
        set((s) => ({ [section]: { ...(s[section] as object), [key]: val } })),
      loadInputs: (inputs) => set({ ...inputs }),
      reset: () => set({ ...DEFAULT_INPUTS }),
      getInputs: (): TCOInputs => {
        const s = get();
        return {
          duty_cycle: s.duty_cycle,
          fleet: s.fleet,
          vehicles: s.vehicles,
          loan: s.loan,
          lease: s.lease,
          analysis_year: s.analysis_year,
          discount_rate: s.discount_rate,
        };
      },
    }),
    { name: 'tco-inputs' }
  )
);

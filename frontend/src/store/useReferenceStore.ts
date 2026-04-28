import { create } from 'zustand';
import { EVVehicle, ICEVehicle, Charger } from '../types/reference';
import { fetchEVVehicles, fetchICEVehicles, fetchChargers } from '../api/vehicles';

interface ReferenceState {
  evVehicles: EVVehicle[];
  iceVehicles: ICEVehicle[];
  chargers: Charger[];
  isLoaded: boolean;
  load: () => Promise<void>;
}

export const useReferenceStore = create<ReferenceState>((set, get) => ({
  evVehicles: [],
  iceVehicles: [],
  chargers: [],
  isLoaded: false,
  load: async () => {
    if (get().isLoaded) return;
    const [ev, ice, chargers] = await Promise.all([
      fetchEVVehicles(),
      fetchICEVehicles(),
      fetchChargers(),
    ]);
    set({ evVehicles: ev, iceVehicles: ice, chargers, isLoaded: true });
  },
}));

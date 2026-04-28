import client from './client';
import { EVVehicle, ICEVehicle, Charger } from '../types/reference';

export async function fetchEVVehicles(category?: string): Promise<EVVehicle[]> {
  const res = await client.get<EVVehicle[]>('/vehicles/ev', { params: category ? { category } : {} });
  return res.data;
}

export async function fetchICEVehicles(category?: string): Promise<ICEVehicle[]> {
  const res = await client.get<ICEVehicle[]>('/vehicles/ice', { params: category ? { category } : {} });
  return res.data;
}

export async function fetchChargers(): Promise<Charger[]> {
  const res = await client.get<Charger[]>('/chargers');
  return res.data;
}

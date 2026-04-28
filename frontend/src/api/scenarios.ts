import client from './client';
import { SavedScenario } from '../types/reference';
import { TCOInputs } from '../types/inputs';

export async function fetchScenarios(): Promise<SavedScenario[]> {
  const res = await client.get<SavedScenario[]>('/scenarios');
  return res.data;
}

export async function fetchScenario(id: number): Promise<{ id: number; name: string; inputs: TCOInputs; result: any }> {
  const res = await client.get(`/scenarios/${id}`);
  return res.data;
}

export async function saveScenario(name: string, inputs: TCOInputs): Promise<{ id: number }> {
  const res = await client.post('/scenarios', { name, ...inputs });
  return res.data;
}

export async function deleteScenario(id: number): Promise<void> {
  await client.delete(`/scenarios/${id}`);
}

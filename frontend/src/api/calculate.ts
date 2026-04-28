import client from './client';
import { TCOInputs } from '../types/inputs';
import { TCOResult } from '../types/outputs';

export async function calculateTCO(inputs: TCOInputs): Promise<TCOResult> {
  const res = await client.post<TCOResult>('/calculate', inputs);
  return res.data;
}

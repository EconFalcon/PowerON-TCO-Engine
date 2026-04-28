import client from './client';
import { TCOInputs } from '../types/inputs';

export async function exportPDF(inputs: TCOInputs): Promise<void> {
  const res = await client.post('/export/pdf', inputs, { responseType: 'blob' });
  const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = 'PowerOn_TCO_Report.pdf';
  a.click();
  URL.revokeObjectURL(url);
}

export function formatCurrency(val: number): string {
  return new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD', maximumFractionDigits: 0 }).format(val);
}

export function formatCurrencyCompact(val: number): string {
  if (Math.abs(val) >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (Math.abs(val) >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return formatCurrency(val);
}

export function formatKm(val: number): string {
  return `$${val.toFixed(3)}/km`;
}

export function formatPct(val: number): string {
  return `${(val * 100).toFixed(1)}%`;
}

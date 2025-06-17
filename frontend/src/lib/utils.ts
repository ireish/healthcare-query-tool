// Helper to aggregate counts and limit to top N, grouping remainder as "Other"
export function topNWithOther(
  counts: Record<string, number>,
  topN: number
): { name: string; value: number }[] {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const top = entries.slice(0, topN);
  const other = entries.slice(topN);
  const data = top.map(([name, value]) => ({ name, value }));
  if (other.length) {
    const otherTotal = other.reduce((sum, [, v]) => sum + v, 0);
    data.push({ name: "Other", value: otherTotal });
  }
  return data;
} 
/**
 * fetchJson — typed fetch with HTTP error checking.
 * Throws on non-2xx responses so callers get consistent error behavior.
 */
export async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${url}`);
  return res.json() as Promise<T>;
}

// Тонкий HTTP-клиент к /api/v1 с JWT и единым форматом ошибок.
const BASE = "/api/v1";

let accessToken: string | null = null;
export const setToken = (t: string | null) => { accessToken = t; };

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) throw Object.assign(new Error("API error"), { status: res.status, body: await res.json().catch(() => null) });
  return res.status === 204 ? (undefined as T) : res.json();
}

const API_BASE = import.meta.env.VITE_API_URL ?? "";

type Options = RequestInit & { headers?: Record<string, string> };

export async function apiFetch<T>(path: string, options: Options = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

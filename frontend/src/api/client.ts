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
    let detailMessage: string | undefined;
    if (typeof body.detail === "string") {
      detailMessage = body.detail;
    } else if (Array.isArray(body.detail)) {
      detailMessage = body.detail
        .map((item: unknown) => {
          if (typeof item === "string") return item;
          if (item && typeof item === "object" && "msg" in item && (item as { msg?: unknown }).msg) {
            return String((item as { msg?: unknown }).msg);
          }
          return JSON.stringify(item);
        })
        .join("; ");
    }
    const error = new Error(detailMessage || `Request failed with status ${response.status}`) as Error & {
      status?: number;
    };
    error.status = response.status;
    throw error;
  }

  return response.json() as Promise<T>;
}

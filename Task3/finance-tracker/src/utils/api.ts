// src/utils/api.ts
/**
 * Simple wrapper around fetch that includes the API key header.
 * Adjust BASE_URL as needed for development or production.
 */
export const BASE_URL = import.meta.env.VITE_BACKEND_URL || 
  (import.meta.env.DEV ? "http://localhost:8000" : "https://finance-tracker-131m.onrender.com");

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const apiKey = import.meta.env.VITE_API_KEY || "";
  const headers = new Headers(options.headers);
  if (apiKey) {
    headers.set("X-API-KEY", apiKey);
  }
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error ${response.status}: ${errorText}`);
  }
  return (await response.json()) as T;
}

// Example usage:
// const transactions = await apiRequest<Transaction[]>("/transactions");

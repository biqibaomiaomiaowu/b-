import type { ApiResponse } from '@/types/api'

const apiBase = import.meta.env.VITE_API_BASE ?? ''

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text()
  if (!text) {
    return {} as T
  }
  return JSON.parse(text) as T
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  return {
    ok: response.ok,
    status: response.status,
    data: await parseJson<T>(response),
  }
}

export function getJson<T>(path: string): Promise<ApiResponse<T>> {
  return requestJson<T>(path, {
    method: 'GET',
  })
}

export function postJson<T>(path: string, payload: unknown): Promise<ApiResponse<T>> {
  return requestJson<T>(path, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

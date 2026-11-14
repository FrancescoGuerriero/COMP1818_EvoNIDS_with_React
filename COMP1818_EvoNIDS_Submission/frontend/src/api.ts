export type ApiConnection = {
  timestamp_utc: string
  protocol: string
  local_address: string
  remote_address: string
  status: string
  pid: number | null
  process_name: string | null
  host_os: string
}

export type ReplayRecord = Record<string, string | number | boolean | null>

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed with HTTP ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string; service: string }>('/api/health'),
  connections: () => request<ApiConnection[]>('/api/connections'),
  replayCsv: (csvText: string) => request<{ rows: ReplayRecord[]; count: number }>('/api/replay', {
    method: 'POST',
    headers: { 'Content-Type': 'text/csv; charset=utf-8' },
    body: csvText,
  }),
}

// Thin, typed fetch wrapper. Uses a relative /api base so the browser talks to
// whatever host served the app (see docs/NETWORK.md) — no hard-coded IPs.
import type {
  BallPayload,
  CreateMatchPayload,
  LiveState,
  MatchDetail,
  MatchListItem,
  OpenersPayload,
} from '../types'

const BASE = '/api'

interface RequestOptions {
  method?: 'GET' | 'POST'
  body?: unknown
}

async function request<T>(path: string, { method = 'GET', body }: RequestOptions = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  const text = await res.text()
  const data = text ? JSON.parse(text) : null
  if (!res.ok) {
    const detail = data?.detail ?? data ?? res.statusText
    throw new Error(Array.isArray(detail) ? detail.join(', ') : String(detail))
  }
  return data as T
}

export const api = {
  listMatches: () => request<MatchListItem[]>('/matches/'),
  getMatch: (id: number | string) => request<MatchDetail>(`/matches/${id}/`),
  createMatch: (payload: CreateMatchPayload) =>
    request<MatchDetail>('/matches/', { method: 'POST', body: payload }),
  getLive: (id: number | string) => request<LiveState>(`/matches/${id}/live/`),
  setOpeners: (id: number | string, payload: OpenersPayload) =>
    request<LiveState>(`/matches/${id}/openers/`, { method: 'POST', body: payload }),
  recordBall: (id: number | string, payload: BallPayload) =>
    request<LiveState>(`/matches/${id}/balls/`, { method: 'POST', body: payload }),
  transitionInnings: (id: number | string, payload: OpenersPayload) =>
    request<LiveState>(`/matches/${id}/innings/transition/`, { method: 'POST', body: payload }),
  finishMatch: (id: number | string) =>
    request<LiveState>(`/matches/${id}/finish/`, { method: 'POST' }),
}

// Thin fetch wrapper. Uses a relative /api base so the browser talks to whatever
// host served the app (see docs/NETWORK.md) — no hard-coded IPs.
const BASE = '/api'

async function request(path, { method = 'GET', body } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  const text = await res.text()
  const data = text ? JSON.parse(text) : null
  if (!res.ok) {
    const detail = data?.detail || data || res.statusText
    throw new Error(Array.isArray(detail) ? detail.join(', ') : String(detail))
  }
  return data
}

export const api = {
  listMatches: () => request('/matches/'),
  getMatch: (id) => request(`/matches/${id}/`),
  createMatch: (payload) => request('/matches/', { method: 'POST', body: payload }),
  getLive: (id) => request(`/matches/${id}/live/`),
  setOpeners: (id, payload) =>
    request(`/matches/${id}/openers/`, { method: 'POST', body: payload }),
  recordBall: (id, payload) =>
    request(`/matches/${id}/balls/`, { method: 'POST', body: payload }),
  transitionInnings: (id, payload) =>
    request(`/matches/${id}/innings/transition/`, { method: 'POST', body: payload }),
  finishMatch: (id) => request(`/matches/${id}/finish/`, { method: 'POST' }),
}

# NETWORK

# Local Network & Field Deployment

> **⚠️ Phase scope note.** This document describes the *full* field-deployment target,
> including real-time WebSockets. **Phase 1 (MVP) does NOT use WebSockets or Django
> Channels** — the Viewer screen refreshes by **polling** `GET /api/matches/{id}/live/`
> every few seconds. Every reference to Channels, ASGI, or `/ws/…` below applies to
> **Phase 3** (Cloud Migration & Global Viewing). The local-network, `cricket.local`,
> hotspot, `0.0.0.0` binding, one-origin, and Docker guidance all apply from Phase 1.

## Overview

The cricket application is designed to run entirely on a local network at the cricket ground.

The MacBook acts as:

- The application server
- The SQLite database host
- The WebSocket server *(Phase 3 only; Phase 1 uses polling)*
- Optionally, the Wi-Fi hotspot/local network

No internet connection is required for scoring or viewing the match.

The preferred field URL is:

```
http://cricket.local/
```

The application should never depend on a hard-coded IP address.

---

## 1. Local Network Topology

Preferred setup:

```
                    MacBook Air
                 cricket.local
                       │
                Local Wi-Fi network
                       │
          ┌────────────┼────────────┐
          │            │            │
       Scorer       Viewer       Viewer
        Phone        Phone        Phone
```

The MacBook runs:

```
Django + DRF
Django Channels
Vue production build
SQLite
```

All devices communicate directly over the local network.

Internet access is not required.

---

## 2. Configure the Mac Local Hostname

macOS provides a local hostname through Bonjour/mDNS.

Apple calls this the **Local hostname**.

### Set the Mac computer name

Open:

```
Apple menu
→ System Settings
→ General
→ About
```

Set the computer name to:

```
Cricket
```

The Mac's local hostname will normally become:

```
Cricket.local
```

macOS replaces spaces with hyphens and local hostnames are case-insensitive. {"fallbackMarkdown":"([Apple Support](https://support.apple.com/en-ca/guide/mac-help/mchlp1177/mac?utm_source=chatgpt.com))","reference":{"matched_text":"","prefix":null,"start_idx":2058,"end_idx":2090,"safe_urls":["https://support.apple.com/en-ca/guide/mac-help/mchlp1177/mac","https://support.apple.com/en-ca/guide/mac-help/mchlp1177/mac?utm_source=chatgpt.com","https://support.apple.com/my-mm/guide/mac-help/mchlp2322/mac","https://support.apple.com/my-mm/guide/mac-help/mchlp2322/mac?utm_source=chatgpt.com"],"refs":[],"alt":"([Apple Support](https://support.apple.com/en-ca/guide/mac-help/mchlp1177/mac?utm_source=chatgpt.com))","prompt_text":null,"type":"grouped_webpages","status":"done","error":null,"fallback_items":null,"style":null,"items":[{"title":"Find your computer’s name and network address on Mac - Apple Support (CA)","url":"https://support.apple.com/en-ca/guide/mac-help/mchlp1177/mac?utm_source=chatgpt.com","attribution":"Apple Support","pub_date":null,"snippet":"","attribution_segments":null,"supporting_websites":[{"title":"Change your computer’s name or local hostname on Mac - Apple support (MM)","url":"https://support.apple.com/my-mm/guide/mac-help/mchlp2322/mac?utm_source=chatgpt.com","pub_date":null,"snippet":"","attribution":"Apple Support"}],"refs":[{"turn_index":0,"ref_type":"search","ref_index":0},{"turn_index":0,"ref_type":"search","ref_index":1}],"hue":null,"attributions":null}]},"showLoginRequiredCard":false}

### Explicitly set the local hostname

Open:

```
Apple menu
→ System Settings
→ General
→ Sharing
```

At the bottom, find:

```
Local hostname
```

Click:

```
Edit
```

Set:

```
cricket.local
```

Save the change.

Apple documents this local hostname as the name advertised to Bonjour-compatible devices on the local network. {"fallbackMarkdown":"([Apple Support](https://support.apple.com/my-mm/guide/mac-help/mchlp2322/mac?utm_source=chatgpt.com))","reference":{"matched_text":"","prefix":null,"start_idx":2438,"end_idx":2457,"safe_urls":["https://support.apple.com/my-mm/guide/mac-help/mchlp2322/mac","https://support.apple.com/my-mm/guide/mac-help/mchlp2322/mac?utm_source=chatgpt.com"],"refs":[],"alt":"([Apple Support](https://support.apple.com/my-mm/guide/mac-help/mchlp2322/mac?utm_source=chatgpt.com))","prompt_text":null,"type":"grouped_webpages","status":"done","error":null,"fallback_items":null,"style":null,"items":[{"title":"Change your computer’s name or local hostname on Mac - Apple support (MM)","url":"https://support.apple.com/my-mm/guide/mac-help/mchlp2322/mac?utm_source=chatgpt.com","attribution":"Apple Support","pub_date":null,"snippet":"","attribution_segments":null,"supporting_websites":[],"refs":[{"turn_index":0,"ref_type":"search","ref_index":1}],"hue":null,"attributions":null}]},"showLoginRequiredCard":false}

### Verify from the Mac

Run:

```bash
scutil --get LocalHostName
```

Expected:

```
cricket
```

You can also check:

```bash
hostname
```

and:

```bash
dns-sd -G v4 cricket.local
```

The exact output may vary depending on the active network.

---

## 3. Mac Wi-Fi Hotspot

The Mac can use macOS Internet Sharing to create a local Wi-Fi network.

Open:

```
Apple menu
→ System Settings
→ General
→ Sharing
→ Internet Sharing
```

Configure the Wi-Fi network with something simple, for example:

```
Network name: Cricket
Security: WPA2/WPA3 Personal
Password: <field password>
```

macOS allows Internet Sharing to be configured under Sharing and lets you select Wi-Fi as the interface used by connected devices. {"fallbackMarkdown":"([Apple Support](https://support.apple.com/en-nz/guide/mac-help/-mchlp1540/mac?utm_source=chatgpt.com))","reference":{"matched_text":"","prefix":null,"start_idx":3189,"end_idx":3209,"safe_urls":["https://support.apple.com/en-nz/guide/mac-help/-mchlp1540/mac","https://support.apple.com/en-nz/guide/mac-help/-mchlp1540/mac?utm_source=chatgpt.com"],"refs":[],"alt":"([Apple Support](https://support.apple.com/en-nz/guide/mac-help/-mchlp1540/mac?utm_source=chatgpt.com))","prompt_text":null,"type":"grouped_webpages","status":"done","error":null,"fallback_items":null,"style":null,"items":[{"title":"Share the internet connection on Mac with other network users - Apple Support (NZ)","url":"https://support.apple.com/en-nz/guide/mac-help/-mchlp1540/mac?utm_source=chatgpt.com","attribution":"Apple Support","pub_date":null,"snippet":"","attribution_segments":null,"supporting_websites":[],"refs":[{"turn_index":0,"ref_type":"search","ref_index":12}],"hue":null,"attributions":null}]},"showLoginRequiredCard":false}

### Important

The application does **not** require internet access.

The objective is simply:

```
Mac
 ↓
local Wi-Fi
 ↓
phones
```

Test that phones can reach the Mac before relying on this setup at a match.

If macOS hotspot/client isolation prevents reliable phone-to-Mac communication on a particular setup, use the fallback topology:

```
Phone hotspot
      ↓
    Mac
      ↓
   phones
```

or a local router.

---

# 4. Application URLs

Production should expose one application origin:

```
http://cricket.local/
```

The same origin provides:

```
/                   Vue application
/api/...            Django REST API
/ws/...             Django WebSocket
```

For example:

```
http://cricket.local/
http://cricket.local/api/matches/
ws://cricket.local/ws/matches/42/
```

The frontend should not hard-code:

```
192.168.x.x
localhost
127.0.0.1
```

---

# 5. Django Binding

Django must listen on all interfaces.

Development:

```bash
python manage.py runserver 0.0.0.0:8000
```

Docker production should also bind Django/ASGI to:

```
0.0.0.0
```

Never use:

```
127.0.0.1
```

for the field server.

`127.0.0.1` only allows connections from the Mac itself.

---

# 6. Vue Development Configuration

During normal development, use separate Vite and Django servers.

Vite should listen externally so phones can be used for development testing:

```jsx
// vite.config.js

import { defineConfig }from 'vite'
import vuefrom '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  server: {
    host: '0.0.0.0',
    port: 5173
  }
})
```

From another device on the same network:

```
http://<mac-ip>:5173
```

---

# 7. Do Not Hard-Code API Hosts in Vue

The frontend should use the current browser host whenever possible.

Do not do this:

```jsx
const API_URL = 'http://192.168.1.15:8000'
```

Do this instead:

```jsx
const API_BASE_URL = '/api'
```

Then:

```jsx
fetch(`${API_BASE_URL}/matches/`)
```

The browser automatically sends the request to the same host that served the Vue application.

Production:

```
http://cricket.local/api/matches/
```

Development can use a Vite proxy so that:

```
http://localhost:5173/api/matches/
```

is forwarded to:

```
http://localhost:8000/api/matches/
```

---

# 8. Vite Development Proxy

Configure Vite with a development-only proxy:

```jsx
// vite.config.js

import { defineConfig }from 'vite'
import vuefrom '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  server: {
    host: '0.0.0.0',
    port: 5173,

    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },

      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true
      }
    }
  }
})
```

The browser therefore only needs to know:

```
localhost:5173
```

while Vite forwards:

```
/api → Django
/ws  → Django Channels
```

This also avoids unnecessary CORS configuration during development.

---

# 9. WebSocket Configuration

The frontend should derive the WebSocket address from the current browser location.

Example:

```jsx
export function createMatchSocket(matchId) {
  const protocol =
    window.location.protocol=== 'https:'
      ? 'wss:'
      : 'ws:'

  return new WebSocket(
    `${protocol}//${window.location.host}/ws/matches/${matchId}/`
  )
}
```

Production:

```
http://cricket.local
```

automatically becomes:

```
ws://cricket.local/ws/matches/42/
```

Development:

```
http://localhost:5173
```

becomes:

```
ws://localhost:5173/ws/matches/42/
```

Vite then proxies the WebSocket to Django.

The application therefore does not need to know the Mac's IP address.

---

# 10. Production Docker Setup

The production container should contain:

```
Django
Django REST Framework
Django Channels
Vue production build
SQLite
```

Build the Vue application:

```bash
pnpm nx run web:build
```

The resulting:

```
apps/web/dist/
```

is copied into the Django production image.

Django serves the Vue application.

The production architecture becomes:

```
                     MacBook
                       │
                  cricket.local
                       │
                  Docker :8000
                       │
             ┌─────────┴─────────┐
             │                   │
          Django             Channels
             │                   │
          DRF API           WebSockets
             │                   │
             └────────┬──────────┘
                      │
                   SQLite
```

Phones only need to open:

```
http://cricket.local/
```

---

# 11. Docker Port Binding

The container must expose Django to the Mac's network.

Example:

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"

    volumes:
      - sqlite_data:/app/data
```

The application server inside the container must listen on:

```
0.0.0.0:8000
```

not:

```
127.0.0.1:8000
```

Then:

```
Phone
  ↓
cricket.local:8000
  ↓
Mac
  ↓
Docker
  ↓
Django
```

---

# 12. Prefer One Production Origin

The ideal production experience is:

```
http://cricket.local/
```

rather than:

```
http://cricket.local:5173/
http://cricket.local:8000/api/
```

The application should expose:

```
/                    Vue
/api/                DRF
/ws/                 WebSockets
```

This means the scorer and spectators only need one URL.

---

# 13. Phone Setup at the Ground

### Step 1 — Start the Mac

Connect the Mac to power if possible.

### Step 2 — Start the local Wi-Fi

Enable the Cricket Wi-Fi network.

### Step 3 — Start Docker

From the repository:

```bash
docker compose up -d --build
```

### Step 4 — Verify locally

On the Mac:

```bash
curl http://localhost:8000/
```

or open:

```
http://cricket.local/
```

### Step 5 — Connect phones

Connect each phone to:

```
Cricket
```

Wi-Fi.

### Step 6 — Open the application

On each phone:

```
http://cricket.local/
```

No internet connection is required.

---

# 14. Field Connectivity Test

Before the match starts, test:

### Mac

```bash
ping cricket.local
```

### Phone

Open:

```
http://cricket.local/
```

### Scorer

Open the scoring screen and record a test ball.

### Viewer

Open the live match screen.

Confirm that the viewer receives the score update through the WebSocket.

---

# 15. Development vs Field Deployment

## Local development

```
Browser
   │
   ▼
localhost:5173
   │
   ├── /api → localhost:8000
   └── /ws  → localhost:8000
                    │
                  Django
                    │
                  SQLite
```

Run:

```bash
docker compose up
```

or run Django/Vite independently during development.

---

## Field deployment

```
Phone
   │
   ▼
cricket.local
   │
   ▼
Docker
   │
   ├── Vue
   ├── DRF
   ├── Channels
   └── SQLite
```

Run:

```bash
docker compose up -d --build
```

Users only need:

```
http://cricket.local/
```

---

# 16. Design Rules

The application must follow these rules:

1. Never hard-code the Mac's IP address in Vue.
2. Never use `localhost` for production phone access.
3. Django/ASGI must bind to `0.0.0.0`.
4. Vue production should use relative `/api` URLs.
5. WebSockets should derive their host from `window.location.host`.
6. Development may use Vite's `/api` and `/ws` proxies.
7. Production should use one application origin.
8. SQLite remains the persistent source of match data.
9. WebSockets are for live updates, not permanent match storage.
10. The application must work with no internet connection.

## Target field experience

```
Turn on Mac
      ↓
Start Cricket Wi-Fi
      ↓
docker compose up -d
      ↓
Phones join Cricket Wi-Fi
      ↓
Open http://cricket.local/
      ↓
Score match
      ↓
Spectators receive live updates
```

The IP address should be an implementation detail, not something the scorer or spectator needs to know.
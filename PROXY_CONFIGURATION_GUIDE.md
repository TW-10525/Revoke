# Proxy Configuration Guide

## Overview

This project uses a **Vite proxy + environment variables** approach for API calls. This ensures:
- ✅ No hardcoded localhost addresses
- ✅ Works on any machine (local, dev tunnel, production)
- ✅ Automatic CORS handling via proxy
- ✅ Clean separation of dev/prod configurations

---

## How It Works

### Development Flow
```
Browser (http://localhost:3000)
    ↓
Vite Server (runs at http://localhost:3000)
    ↓
Vite Proxy intercepts /api/* calls
    ↓
Rewrites to http://localhost:8000/*
    ↓
Backend (FastAPI at http://localhost:8000)
```

### Dev Tunnel Flow
```
Browser (https://kgqmkjv3.asse.devtunnels.ms:3000)
    ↓
Vite Server (runs via tunnel)
    ↓
Vite Proxy intercepts /api/* calls
    ↓
Rewrites to http://localhost:8000/* (LOCAL, not tunnel)
    ↓
Backend (FastAPI at http://localhost:8000)
```

### Production Flow
```
Browser (https://yourdomain.com)
    ↓
React App (built and served via nginx/CDN)
    ↓
API calls go directly to https://api.yourdomain.com
    ↓
Backend (actual domain, no proxy needed)
```

---

## Files Involved

### 1. `vite.config.js` (Dev Proxy Configuration)
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false
    }
  }
}
```
**What it does:**
- Intercepts all requests to `/api/*`
- Rewrites them to `http://localhost:8000/*`
- Works ONLY during development (`npm run dev`)
- NOT included in production build

### 2. `.env.development` (Dev Environment)
```
VITE_API_URL=/api
```
**When used:** `npm run dev`  
**What it does:** Sets API URL to `/api` to use the Vite proxy

### 3. `.env.production` (Production Environment)
```
VITE_API_URL=https://api.yourdomain.com
```
**When used:** `npm run build` (build time)  
**What it does:** Sets API URL to actual backend domain for production

### 4. `src/services/api.js` (API Client)
```javascript
const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
});
```
**What it does:**
- Reads `VITE_API_URL` from environment
- Creates axios instance with correct baseURL
- All API calls use this instance automatically

---

## How to Use

### Running Development Server
```bash
cd frontend
npm run dev
```
- Vite loads `.env.development`
- `VITE_API_URL=/api` is set
- Proxy automatically handles `/api/*` → `localhost:8000/*`

### Building for Production
```bash
cd frontend
npm run build
```
- Vite loads `.env.production`
- `VITE_API_URL=https://api.yourdomain.com` is baked into build
- No proxy needed (React serves from same domain)

### Testing with Dev Tunnel
```bash
cd frontend
npm run dev
# Tunnel runs on https://kgqmkjv3.asse.devtunnels.ms:3000
```
- Frontend goes through tunnel
- But `/api` calls still go to `localhost:8000` (local backend)
- Proxy handles it seamlessly

---

## Key Points

### ✅ What You Get

| Scenario | Works? | How? |
|----------|--------|------|
| Local dev (localhost:3000 → localhost:8000) | ✅ | Vite proxy rewrites `/api` |
| Dev tunnel (tunnel → localhost:8000) | ✅ | Vite proxy still rewrites `/api` |
| Different machine (dev tunnel both) | ✅ | Vite proxy local to each machine |
| Production (yourdomain.com → api.yourdomain.com) | ✅ | No proxy, direct CORS-safe call |

### ❌ What NOT to Do

```javascript
// ❌ WRONG - hardcoded localhost
axios.post('http://localhost:8000/token')

// ✅ RIGHT - uses proxy or env var
api.post('/token')  // api instance handles baseURL
```

### 🔍 Debugging

**Check if proxy is working:**
1. Open DevTools → Network tab
2. Try to log in
3. Look for request URL:
   - ✅ Correct: `https://kgqmkjv3.asse.devtunnels.ms:3000/api/token` (shows /api)
   - ❌ Wrong: `http://localhost:8000/token` (hardcoded)

**If you see hardcoded localhost:**
```bash
grep -R "localhost:8000" frontend/src/
```
Replace all occurrences with `/api/...`

---

## Customizing for Your Setup

### For Production Deployment

1. **Update `.env.production`:**
```bash
VITE_API_URL=https://your-backend-domain.com
```

2. **Ensure your backend CORS allows your frontend domain:**
```python
origins = [
    "https://your-frontend-domain.com",
    "https://api.your-domain.com",
]
```

3. **Build and deploy:**
```bash
npm run build
# Deploy dist/ folder to your hosting
```

### For Multiple Environments

Create multiple env files:
- `.env.development` (local dev)
- `.env.staging` (staging backend)
- `.env.production` (production backend)

Vite automatically selects based on environment.

---

## Why This Approach?

| Aspect | Nginx | This Solution |
|--------|-------|----------------|
| Setup complexity | High | Low |
| Maintenance | Medium | Low |
| Works with dev tunnel | Maybe | ✅ YES |
| Works on any machine | Maybe | ✅ YES |
| Production ready | ✅ | ✅ |
| Learning curve | High | Low |
| CORS handling | Manual | Automatic |

**This solution is:**
- Simple to understand
- Built into Vite (zero extra tools)
- Works immediately
- Scales to production
- Requires no system administration

---

## Summary

```mermaid
┌─────────────────────────────────────┐
│     npm run dev                     │
│  (.env.development loaded)          │
├─────────────────────────────────────┤
│ VITE_API_URL = /api                 │
│ Vite Proxy: /api → localhost:8000   │
│                                     │
│ Result: No CORS, works everywhere   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     npm run build                   │
│  (.env.production loaded)           │
├─────────────────────────────────────┤
│ VITE_API_URL = https://api.you...   │
│ No proxy (production doesn't need it)|
│                                     │
│ Result: Direct API calls to backend │
└─────────────────────────────────────┘
```

Done! 🎉

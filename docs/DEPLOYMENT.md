# Deployment Guide

## Step 1 — Deploy Backend on Railway

1. Push the `backend/` folder to a GitHub repo (or the whole project).
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo.
3. Select the repo. Set the **root directory** to `backend/`.
4. Add a **PostgreSQL** plugin: Railway dashboard → Add Plugin → PostgreSQL.
5. Add a **Redis** plugin: Railway dashboard → Add Plugin → Redis.
6. Set environment variables in Railway:

```
SECRET_KEY=<generate a random 50-char string>
DEBUG=False
ALLOWED_HOSTS=<your-railway-app>.up.railway.app
CORS_ALLOWED_ORIGINS=https://<your-vercel-app>.vercel.app
DATABASE_URL=<auto-set by Railway PostgreSQL plugin>
REDIS_URL=<auto-set by Railway Redis plugin>
```

7. Railway will detect the `Dockerfile` and deploy automatically.
8. On first deploy, run migrations via Railway shell:
   ```bash
   python manage.py migrate
   ```
   Or add `release: python manage.py migrate` to `Procfile` (already done).

9. Note your Railway backend URL: `https://your-app.up.railway.app`

---

## Step 2 — Deploy Frontend on Vercel

1. Push the `frontend/` folder to GitHub (or the full project).
2. Go to [vercel.com](https://vercel.com) → New Project → Import from GitHub.
3. Set **Root Directory** to `frontend/`.
4. Add environment variables:

```
VITE_API_URL=https://your-app.up.railway.app
VITE_WS_URL=wss://your-app.up.railway.app
```

> **Note**: Use `wss://` (secure WebSocket) for production since Railway serves over HTTPS.

5. Click Deploy. Vercel auto-detects Vite.
6. Note your Vercel frontend URL: `https://your-app.vercel.app`

---

## Step 3 — Update CORS on Backend

Go back to Railway env vars and set:
```
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
```

Redeploy backend.

---

## Step 4 — Verify

- Visit `https://your-app.vercel.app` → should load login page
- Register a user → should redirect to dashboard
- Create a group → invite another user
- Add expense → see balance update
- Open expense detail → chat should connect (green dot)

---

## Local Development Quick Start

```bash
# Terminal 1 — Start PostgreSQL and Redis (Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
docker run -d -p 6379:6379 redis:7

# Terminal 2 — Backend
cd backend
cp .env.example .env   # edit DATABASE_URL if needed
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Terminal 3 — Frontend
cd frontend
npm install
cp .env.example .env   # VITE_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:5173

# SplitEase — Splitwise Clone + CSV Expense Importer

A full-stack expense sharing app with CSV anomaly detection, built for the Spreetail internship assignment.

## AI Used
**Claude (claude-sonnet-4-6)** by Anthropic — primary development collaborator.

## Live Demo
- **Frontend**: https://your-app.vercel.app  *(replace after deploy)*
- **Backend API**: https://your-api.up.railway.app  *(replace after deploy)*

---

## Deliverables Checklist
- [x] Public deployed app URL
- [x] GitHub repository with meaningful commit history
- [x] `README.md` — setup instructions and AI used
- [x] `SCOPE.md` — anomaly log + database schema
- [x] `DECISIONS.md` — decision log with options considered
- [x] Import report — produced by app when ingesting CSV (downloadable from /import page)
- [x] `AI_USAGE.md` — AI tool used, key prompts, 3 cases where AI was wrong

---

## Features

### Splitwise Core
- Email/password auth with JWT
- Create and manage groups (invite by email, remove members, admin roles)
- Create expenses with 4 split types: equal, unequal, percentage, shares
- Real-time chat on each expense (WebSocket)
- Group-wise balance summary
- Overall balance dashboard across all groups
- Settle up — record payments between users

### CSV Import (Updated Assignment)
- Upload `Expenses_Export.csv` via drag-and-drop
- Detects 20+ anomaly types automatically
- Stores clean data in relational DB (PostgreSQL)
- Full import report with every anomaly, action taken, skipped rows
- Download report as a text file

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, Django REST Framework, Django Channels |
| Database | PostgreSQL (relational, required by assignment) |
| Cache/PubSub | Redis (for WebSocket) |
| Frontend | React 18, Vite, Tailwind CSS |
| Auth | JWT (simplejwt) |
| Deploy | Railway (backend + DB + Redis) + Vercel (frontend) |

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node 18+
- PostgreSQL running locally
- Redis running locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit with your local DB credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # set VITE_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:5173

---

## Environment Variables

### Backend (`backend/.env`)
```
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgres://postgres:password@localhost:5432/splitwise
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (`frontend/.env`)
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## Project Files

| File | Purpose |
|------|---------|
| `AI_CONTEXT.md` | Full context used to build this app with AI |
| `BUILD_PLAN.md` | Architecture, research, and AI collaboration notes |
| `SCOPE.md` | Anomaly log (every CSV problem found) + DB schema |
| `DECISIONS.md` | Every significant decision and why |
| `AI_USAGE.md` | AI tool used, key prompts, 3 AI mistakes caught |
| `backend/` | Django project |
| `frontend/` | React + Vite app |
| `docs/DEPLOYMENT.md` | Step-by-step Railway + Vercel deployment guide |

# DECISIONS.md — Decision Log

Every significant decision made during this project, the options considered, and why a specific choice was made.

---

## 1. Framework Choice: Django REST Framework

**Decision:** Use Django + Django REST Framework for the backend.

**Options considered:**
- FastAPI — faster, async-native, but less mature ORM and admin
- Flask — lightweight but too bare; would need more boilerplate
- Django DRF — batteries included, excellent ORM, built-in admin, simplejwt

**Why Django DRF:** The assignment asked for Python. Django's ORM makes relational schema design clean. The admin panel gives instant visibility into DB state during development. DRF's serializers handle validation well for expense split logic.

---

## 2. Real-time Chat: Django Channels + Redis

**Decision:** WebSocket via Django Channels with Redis as the channel layer.

**Options considered:**
- Polling every 3 seconds — simple but not real-time, wastes requests
- Server-Sent Events (SSE) — one-directional, can't send from client
- WebSocket with Channels — true bi-directional real-time

**Why Channels + Redis:** Actual real-time requirement stated in the assignment. Redis as channel layer is the standard pairing. Redis is available free on Railway.

**Trade-off accepted:** WebSocket auth is done via `?token=` query parameter (not headers) because browsers cannot set custom headers on WebSocket upgrades. This is a known and acceptable pattern.

---

## 3. Authentication: JWT (not sessions)

**Decision:** Use JWT tokens stored in `localStorage` via `simplejwt`.

**Options considered:**
- Django sessions + CSRF — works well with server-rendered apps, fragile with React
- JWT in HttpOnly cookies — more secure against XSS but CORS cookie handling is complex
- JWT in localStorage — simpler, standard for SPAs

**Why JWT in localStorage:** Faster to build correctly. The assignment is time-boxed to 2 days. HttpOnly cookies would require additional CSRF configuration. JWT is acceptable for an internship assignment scope.

---

## 4. Split Logic: Compute at Save Time

**Decision:** Compute each member's exact owed amount when the expense is saved, store in `expense_splits.amount`.

**Options considered:**
- Recompute on every balance read — flexible if rules change, but slow and complex
- Store raw inputs only (%, shares) — need extra computation on every API call
- Store computed amounts — fast reads, simple balance calculation

**Why compute at save:** Balance queries are frequent (shown on every group page). Pre-computing means balance calculation is a simple sum, not a recalculation. If an expense needs to change, it is deleted and recreated (stated trade-off).

---

## 5. Balance Calculation: Direct Pairs (No Simplification)

**Decision:** Show direct debts between every pair of people, without running a debt-simplification algorithm.

**Options considered:**
- Debt graph simplification (greedy min-cash-flow) — A owes B ₹100, B owes C ₹100 → A owes C ₹100 directly
- Direct pair calculation — show every raw debt without simplification

**Why direct pairs:** Debt simplification requires a more complex algorithm. For the MVP time constraint, direct pairs are correct (if not optimal). Documented as a known limitation in `AI_CONTEXT.md`.

---

## 6. Database: PostgreSQL Only (Relational)

**Decision:** PostgreSQL for all data storage.

**Options considered:**
- SQLite — fine for dev, not suitable for production multi-user
- MongoDB — not relational, violates the assignment requirement
- PostgreSQL — relational, supports JSONB (used for `split_details`), Railway managed addon

**Why PostgreSQL:** Assignment explicitly states "Use relational DBs only." PostgreSQL is the production-grade choice. The `split_details` JSONB field stores flexible split configurations without breaking relational schema principles.

---

## 7. Deployment: Railway (backend) + Vercel (frontend)

**Decision:** Railway for Django/Postgres/Redis, Vercel for React.

**Options considered:**
- Heroku — had free tier until 2022, now paid
- Render — similar to Railway, slightly less Redis support
- AWS EC2 — powerful but complex, overkill for an internship assignment
- Railway + Vercel — both have free tiers, Railway manages PostgreSQL + Redis as addons

**Why Railway + Vercel:** Fastest path to a working public URL with zero cost. Railway auto-detects Dockerfile. Vercel auto-detects Vite/React. Deployment takes ~10 minutes.

---

## 8. CSV Import: Server-side Processing (Not Frontend)

**Decision:** The CSV is uploaded to Django, processed by the Python engine, stored in DB, and the report is returned as JSON.

**Options considered:**
- Parse CSV entirely in the browser (JavaScript) — no backend storage, not re-auditable
- Parse in backend, store in DB — full audit trail, import history, re-queryable

**Why backend processing:** The assignment requires a stored "import report." The report must be reproducible. Server-side also allows for consistent anomaly detection logic in one place (Python, not duplicated in JS).

---

## 9. USD Conversion: Fixed Rate

**Decision:** Convert USD amounts at a fixed rate of ₹84/USD.

**Options considered:**
- Live exchange rate API — accurate but needs API key, network call, error handling
- Fixed rate — simpler, documented, deterministic

**Why fixed rate:** Live FX is out of scope for a 2-day assignment. Fixed rate is documented in `engine.py` as a named constant (`USD_TO_INR = 84.0`) so it can be changed in one place. The anomaly report flags all converted rows so reviewers can see what was converted.

---

## 10. Stale Member Cutoff: April 1, 2026

**Decision:** Meera is treated as having left the group on March 28, 2026. Any expense dated April 1 or later that includes Meera in `split_with` removes her automatically.

**Options considered:**
- Remove Meera from all splits — too aggressive; her March expenses are valid
- Flag but keep Meera — leaves incorrect data
- Remove from April onwards — matches the CSV note about her moving out

**Why April 1 cutoff:** Row 36 in the CSV explicitly says "oops Meera still in group list" for an April expense. March 28 is her last valid expense date. A clean cutoff at April 1 is deterministic and logged.

---

## 11. Duplicate Detection: Fingerprint + Fuzzy Match

**Decision:** Use a two-level duplicate check: (a) exact fingerprint match → skip; (b) fuzzy same-date-same-amount-similar-description → warn but import.

**Options considered:**
- Exact match only — misses fuzzy duplicates like "Thalassa dinner" vs "dinner thalassa"
- Edit distance (Levenshtein) — accurate but complex to implement in time
- Substring match — sufficient for the data patterns in this CSV

**Why two-level:** Exact match is unambiguous — skip with confidence. Fuzzy match is uncertain — import with a warning so a human reviewer can decide. Never silently drop data that might be legitimate.

---

## 12. Expense Editing: Not Supported

**Decision:** Expenses cannot be edited after creation. Users must delete and re-create.

**Options considered:**
- Full edit support — requires re-computing all splits, checking balance impacts
- Soft delete + new version — complex audit trail
- Delete and recreate — simple, honest

**Why no edit:** Time constraint. Balance calculation correctness is easier to guarantee when splits are immutable. Documented as known limitation.

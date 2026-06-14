# AI_CONTEXT.md — Splitwise Clone

> **Source of Truth** for the entire project.  
> Maintained collaboratively between the developer and AI (Claude).  
> Another developer or AI agent should be able to read this file and recreate a functionally similar app.

---

## 1. Product Understanding

### What is Splitwise?
Splitwise is an expense-sharing app that helps groups of people track shared costs and settle debts.  
Core user flows:
- Users form groups (trips, households, couples)
- Anyone in the group adds an expense (e.g. "Dinner – ₹1200")
- The app calculates who owes whom based on split rules
- Users settle debts (record a payment), zeroing out or reducing balances
- A chat thread lives inside each expense for discussion

### Product Research Findings
- Groups can be "trip", "home", "other" categorized
- Expenses can be split: equally / unequally (exact amounts) / by percentage / by shares
- Balance simplification: rather than A→B and B→C, Splitwise simplifies to A→C
- Settle-up is separate from expense creation — it is a payment record
- Real-time chat is scoped per expense (not per group)
- A user's "dashboard" shows net balance across ALL groups

---

## 2. Product Scope (MVP)

### In Scope
- Email/password authentication (JWT)
- User profile (name, email, avatar initial)
- Create / view / leave / delete groups
- Invite members by email; group admin can remove members
- Create expenses with 4 split modes
- View expenses list per group
- Expense detail with comment/chat (real-time via WebSocket)
- Group balance summary (who owes whom inside the group)
- Individual overall balance summary across all groups
- Settle up: record a manual payment between two users
- Relational DB (PostgreSQL)

### Out of Scope (explicitly)
- Email notifications / OTP
- Mobile app
- Currency conversion
- Recurring expenses
- Receipt photo upload
- OAuth (Google / Facebook login)
- Push notifications
- Expense categories / icons
- Balance simplification algorithm (kept simple: direct debt pairs)

---

## 3. User Personas

| Persona | Description |
|---------|-------------|
| Group Admin | Creates the group, invites members, can remove members |
| Group Member | Adds expenses, settles debts, chats |
| Observer | Added to a group but hasn't interacted yet |

---

## 4. Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Backend framework | Django + Django REST Framework | Python, clean ORM, assignment asks Python |
| Real-time | Django Channels + Redis | WebSocket for expense chat |
| Database | PostgreSQL | Relational DB requirement |
| Auth | JWT via `djangorestframework-simplejwt` | Stateless, easy to use with React |
| Frontend | React 18 + Vite | Fast, component-based |
| Styling | Tailwind CSS | Utility-first, fast prototyping |
| State | React Context + hooks | Lightweight, no Redux overhead |
| HTTP client | Axios | Interceptors for JWT refresh |
| WebSocket client | native browser WebSocket | No extra library needed |
| Deployment (backend) | Railway or Render (Docker) | Free tier, supports PostgreSQL + Redis |
| Deployment (frontend) | Vercel | Free, instant React deploys |

---

## 5. Database Schema

### `users`
```
id          UUID  PK
email       VARCHAR UNIQUE NOT NULL
name        VARCHAR NOT NULL
password    VARCHAR (hashed)
created_at  TIMESTAMP
```

### `groups`
```
id          UUID  PK
name        VARCHAR NOT NULL
description VARCHAR
created_by  FK → users
created_at  TIMESTAMP
```

### `group_members`
```
id          UUID  PK
group       FK → groups
user        FK → users
role        ENUM('admin','member')
joined_at   TIMESTAMP
UNIQUE(group, user)
```

### `expenses`
```
id            UUID  PK
group         FK → groups
title         VARCHAR NOT NULL
amount        DECIMAL(12,2) NOT NULL
paid_by       FK → users
split_type    ENUM('equal','unequal','percentage','shares')
created_by    FK → users
created_at    TIMESTAMP
```

### `expense_splits`
```
id          UUID  PK
expense     FK → expenses
user        FK → users
amount      DECIMAL(12,2)   -- exact owed amount computed at save time
share       DECIMAL(10,4)   -- used for percentage/shares input
```

### `settlements`
```
id          UUID  PK
group       FK → groups
paid_by     FK → users
paid_to     FK → users
amount      DECIMAL(12,2)
note        VARCHAR
created_at  TIMESTAMP
```

### `expense_comments`
```
id          UUID  PK
expense     FK → expenses
user        FK → users
text        TEXT
created_at  TIMESTAMP
```

---

## 6. API Design

### Auth
| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/auth/register/ | Register |
| POST | /api/auth/login/ | Login → returns JWT |
| POST | /api/auth/refresh/ | Refresh token |
| GET  | /api/auth/me/ | Current user profile |

### Groups
| Method | URL | Description |
|--------|-----|-------------|
| GET    | /api/groups/ | List my groups |
| POST   | /api/groups/ | Create group |
| GET    | /api/groups/:id/ | Group detail |
| PATCH  | /api/groups/:id/ | Update group |
| DELETE | /api/groups/:id/ | Delete group (admin) |
| POST   | /api/groups/:id/invite/ | Invite by email |
| DELETE | /api/groups/:id/members/:uid/ | Remove member |

### Expenses
| Method | URL | Description |
|--------|-----|-------------|
| GET    | /api/groups/:id/expenses/ | List expenses in group |
| POST   | /api/groups/:id/expenses/ | Create expense |
| GET    | /api/expenses/:id/ | Expense detail + splits |
| PATCH  | /api/expenses/:id/ | Update expense |
| DELETE | /api/expenses/:id/ | Delete expense |
| GET    | /api/expenses/:id/comments/ | List comments |
| POST   | /api/expenses/:id/comments/ | Post comment |

### Balances
| Method | URL | Description |
|--------|-----|-------------|
| GET    | /api/groups/:id/balances/ | Group-wise balance matrix |
| GET    | /api/balances/ | My overall balance summary |

### Settlements
| Method | URL | Description |
|--------|-----|-------------|
| GET    | /api/groups/:id/settlements/ | List settlements |
| POST   | /api/groups/:id/settlements/ | Record a settlement |

### WebSocket
```
ws://host/ws/expenses/<expense_id>/
```
Events:
- `chat.message` → broadcast new comment to all connected clients
- `chat.history` → send last 50 comments on connect

---

## 7. Frontend Structure

```
src/
├── context/
│   ├── AuthContext.jsx       # JWT state, login/logout
│   └── SocketContext.jsx     # WebSocket connection manager
├── hooks/
│   ├── useAuth.js
│   ├── useGroups.js
│   ├── useExpenses.js
│   └── useBalances.js
├── services/
│   ├── api.js                # Axios instance with JWT interceptor
│   ├── authService.js
│   ├── groupService.js
│   ├── expenseService.js
│   └── settlementService.js
├── pages/
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── DashboardPage.jsx
│   ├── GroupDetailPage.jsx
│   ├── ExpenseDetailPage.jsx
│   └── SettlePage.jsx
├── components/
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   └── RegisterForm.jsx
│   ├── layout/
│   │   ├── Navbar.jsx
│   │   ├── Sidebar.jsx
│   │   └── ProtectedRoute.jsx
│   ├── groups/
│   │   ├── GroupCard.jsx
│   │   ├── GroupList.jsx
│   │   ├── CreateGroupModal.jsx
│   │   └── InviteMemberModal.jsx
│   ├── expenses/
│   │   ├── ExpenseCard.jsx
│   │   ├── ExpenseList.jsx
│   │   ├── CreateExpenseModal.jsx
│   │   └── SplitEditor.jsx
│   ├── chat/
│   │   ├── ChatBox.jsx
│   │   └── ChatMessage.jsx
│   └── settlements/
│       ├── BalanceSummary.jsx
│       └── SettleForm.jsx
```

---

## 8. Split Logic (Backend)

### Equal
`amount_per_person = total / count(members)`

### Unequal (exact)
User provides exact amounts per member. Sum must equal total.

### Percentage
User provides % per member. Sum must equal 100. `amount = total * pct / 100`

### Shares
User provides share weight per member. `amount = total * (my_shares / total_shares)`

All split amounts stored in `expense_splits.amount` after computation.

---

## 9. Balance Calculation

For a group:
```
For each expense:
  paid_by gets +amount
  each split member gets -split.amount

For each settlement:
  paid_by gets +amount
  paid_to gets -amount

Net balance per user = sum of above
```

Balance matrix: for every pair (A, B), `A owes B = sum of B's claims against A`.

---

## 10. Deployment Plan

### Backend (Railway)
- Dockerfile: Python 3.11 + gunicorn + daphne (ASGI)
- Environment variables: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ORIGIN`
- PostgreSQL: Railway managed addon
- Redis: Railway managed addon

### Frontend (Vercel)
- `VITE_API_URL` = backend Railway URL
- `VITE_WS_URL` = ws:// backend URL

---

## 11. Testing Plan

- Backend: Django `TestCase` for models + API endpoint smoke tests
- Frontend: Manual browser testing for all flows
- WebSocket: Tested manually with two browser tabs open

---

## 12. Known Limitations

- No balance simplification (A→B→C not simplified to A→C)
- No email invites — invite by email looks up existing users only
- WebSocket has no auth middleware (token passed as query param)
- No pagination on expense lists
- No expense editing after creation (delete + recreate)

---

## 13. Trade-offs

| Decision | What we chose | What we skipped | Why |
|----------|--------------|-----------------|-----|
| Simplification | Direct debt pairs | Debt graph simplification | Complexity vs. time |
| Real-time | WebSocket per expense | Global notification socket | Simpler scope |
| Auth | JWT only | OAuth | Faster to build |
| Deploy | Railway + Vercel | AWS/GCP | Free tier, faster |

---

## 14. Prompts Used

### Initial Prompt (as required by assignment)
> "You are a junior engineer helping me complete an internship assignment. The assignment is to reverse engineer Splitwise, scope a realistic 3-day version, and build a working deployed app. Do not assume product requirements. Do not jump directly into implementation. Ask me detailed questions about product scope, UX, workflows, edge cases, and engineering decisions..."

### Follow-up prompts included:
- "Use PostgreSQL, Django REST Framework, React with Vite and Tailwind"
- "Split types: equal, unequal, percentage, shares — store computed amounts in DB"
- "Real-time chat per expense using Django Channels + Redis WebSocket"
- "JWT auth. Store token in localStorage. Axios interceptor for refresh."
- "Balance = paid_by credit minus split_amount debit, net per user per group"
- "Settle up creates a settlement record; affects balance calculation"

---

## 15. Changes During Implementation

| Date | Change |
|------|--------|
| Day 1 | Added `role` field to group_members to differentiate admin |
| Day 1 | Decided expense editing is out of scope; delete+recreate instead |
| Day 2 | WebSocket auth via query param `?token=` instead of header |
| Day 2 | Added `note` field to settlements |
| Day 2 | Overall balance page added (was originally only group balance) |

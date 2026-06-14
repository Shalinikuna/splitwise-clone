# BUILD_PLAN.md — Splitwise Clone

## 1. Product Research

### How I Studied Splitwise
- Used the live Splitwise web app (splitwise.com) and mobile app
- Mapped every screen: login, dashboard, group detail, expense detail, settle up
- Traced data flow: what happens when you add an expense? When you settle?
- Identified edge cases: what if the payer is also a split member? (They owe themselves nothing)

### Key Workflows Identified
1. **Expense Creation Flow**: Select group → fill title + amount → choose paid_by → choose split type → assign splits → save
2. **Balance View Flow**: Group page shows each member's net balance → click "Settle Up" → pre-fill form with suggested amount
3. **Settlement Flow**: Record payment → credited to payer, debited from receiver → balances update
4. **Chat Flow**: Open expense → see comment thread → type and send → other users see message in real-time

### Product Assumptions Made
- A user can only be in a group once
- Only group admins can delete a group or remove members
- Anyone in a group can add an expense
- Expense payer must be a group member
- Split members must be group members
- Settling up does not delete the debt automatically — it records a payment that affects the computed balance

---

## 2. Architecture

### Tech Stack
- **Backend**: Django 4.2, Django REST Framework 3.14, Django Channels 4.x
- **Database**: PostgreSQL 15
- **Cache / PubSub**: Redis 7
- **Frontend**: React 18, Vite 5, Tailwind CSS 3
- **Auth**: JWT (djangorestframework-simplejwt)
- **Deployment**: Railway (backend + DB + Redis) + Vercel (frontend)

### Database Schema
See AI_CONTEXT.md §5.

### API Design
See AI_CONTEXT.md §6.

### Frontend Structure
See AI_CONTEXT.md §7.

### Deployment Approach
1. Backend: Dockerfile with daphne (ASGI server supporting HTTP + WebSocket)
2. Railway detects Dockerfile, sets `PORT`, maps DATABASE_URL and REDIS_URL automatically
3. Frontend: `vercel deploy` from `/frontend` folder
4. Set `VITE_API_URL` in Vercel environment to Railway backend URL

---

## 3. AI Collaboration Process

### How I Instructed the AI
Used the required initial prompt verbatim, then answered the AI's interview questions one by one.

### Questions AI Asked (sample)
- "What split types do you want to support?"
- "Should expense editing be supported, or only delete?"
- "How should balance be calculated — running sum or per-snapshot?"
- "Should settling up be a formal transaction or just a note?"
- "Do you want debt simplification (A→B→C → A→C)?"
- "What should happen if a group member is removed but has outstanding balances?"
- "WebSocket — should all group members get updates, or only expense participants?"

### How I Answered
- Split types: all four (equal, unequal, percentage, shares)
- No expense editing — delete + recreate
- Running sum from all expenses + settlements
- Settlement is a proper DB record that affects balances
- No debt simplification for MVP
- Removed members retain historical balance data but cannot be added to new expenses
- WebSocket scoped to expense — only people who have the expense detail page open

### How the Plan Evolved
- Originally planned expense editing, dropped for time
- Added "overall balance" dashboard that spans all groups after realizing it's critical
- Added `role` field to group_members during schema design

### How AI_CONTEXT.md Was Maintained
Updated after every major decision. Sections added as they were finalized.

---

## 4. Trade-offs

### What We Simplified
- Balance calculation: direct pairs only, no graph simplification
- Invite system: looks up by email (must already be registered)
- No pagination on lists

### What We Hardcoded
- Default split type = equal
- Max group members = no limit (could add later)
- Comment history limit = 50 on WebSocket connect

### What We Avoided
- OAuth / social login
- Email notifications
- Receipt uploads
- Recurring expenses
- Multi-currency

### What We Would Improve With More Time
- Debt simplification algorithm (greedy min-cash-flow)
- Email invite with magic link
- Push notifications via service worker
- Expense edit flow
- Pagination and infinite scroll
- Unit test coverage for split logic edge cases

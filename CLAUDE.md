# SampleApp - Claude Code Context

## Project Overview

SampleApp is a Sample Application Template

**MVP Target: December 15, 2025 (2 days)**

## Tech Stack

- **Backend**: Python 3.12 + FastAPI
- **Frontend**: Next.js 16 (React, TypeScript)
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **ORM**: SQLAlchemy 2.0 + Alembic migrations
- **Task Queue**: Celery with Redis broker
- **Deployment**: Docker Compose
- **Architecture**: REST + gRPC

## Project Structure

```
cloudpe/
├── CLAUDE.md                 # This file
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # DB connection
│   │   │
│   │   ├── models/          # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── vm.py
│   │   │   ├── pricing.py
│   │   │   └── billing.py
│   │   │
│   │   ├── schemas/         # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── vm.py
│   │   │   └── pricing.py
│   │   │
│   │   ├── api/             # API routes
│   │   │   ├── __init__.py
│   │   │   ├── deps.py      # Dependencies (auth, db session)
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   └── admin/
│   │   │       ├── __init__.py
│   │   │       ├── users.py
│   │   │       └── pricing.py
│   │   │
│   │   ├── services/        # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   └── user_service.py
│   │   │
│   │   ├── tasks/           # Celery tasks
│   │   │   └── __init__.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── security.py  # Password hashing, JWT
│   │       └── exceptions.py
│   │
│   ├── alembic/             # DB migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
│
├── frontend/                 # Next.js 16 Frontend
│   ├── src/
│   │   ├── app/             # App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── signup/page.tsx
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx
│   │   │   │   ├── users/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── [id]/page.tsx
│   │   │   │   │   └── create/page.tsx
│   │   │   │   └── settings/page.tsx
│   │   │   └── admin/
│   │   │       ├── layout.tsx
│   │   │       ├── page.tsx
│   │   │       └── users/page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ui/          # Shadcn/ui components
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── DashboardLayout.tsx
│   │   │   └── users/
│   │   │       ├── userList.tsx
│   │   │       ├── userCard.tsx
│   │   │       ├── CreateUserForm.tsx
│   │   │       └── userConsole.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts       # API client (fetch wrapper)
│   │   │   ├── auth.ts      # Auth utilities
│   │   │   └── utils.ts
│   │   │
│   │   └── types/
│   │       └── index.ts     # TypeScript types
│   │
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile
│
└── docs/
    └── prd/                 # PRD documents for reference
```

## Commands Reference

```bash
# Start development
docker compose up -d

# Run migrations
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Backend logs
docker compose logs -f backend

# Frontend logs
docker compose logs -f frontend

# Access DB
docker compose exec db psql -U cloudpe -d cloudpe

# Run tests
docker compose exec backend pytest
```

## Code Style

### Python

- Use type hints everywhere
- Use async/await for IO operations
- Use Pydantic for validation
- Follow PEP 8

### TypeScript

- Strict mode enabled
- Use interfaces for API responses
- Use React Query or SWR for data fetching
- Use Tailwind CSS for styling

## MVP Features

- Database driven configuration
- User signup/login with JWT authentication
- Admin panel for users
- Multi-region support
- Email notifications
- 2FA authentication

## Priority Order (MVP)

1. **Backend Setup** - FastAPI app, database, Docker
1. **Auth** - Signup, login, JWT middleware, Profile & password update
1. **Frontend Setup** - Next.js, Tailwind, shadcn/ui
1. **Auth UI** - Login, signup, reset password pages
1. **Admin** - Users views, Application Configuration
1. **Polish** - Error handling, loading states, store logs rotating log files

## Notes for Claude

- Always use async/await in Python backend
- Use SQLAlchemy 2.0 style (not legacy 1.x)
- Use Pydantic v2 for schemas
- Frontend uses App Router (not Pages Router)
- Use server components where possible in Next.js
- Keep MVP simple - no over-engineering
- Add API into ./docs/api/\*.rest (REST CLIENT vscode extention)

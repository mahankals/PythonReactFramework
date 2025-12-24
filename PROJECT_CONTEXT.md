# SampleApp - Claude Code Context

## Project Overview

SampleApp is a Full-Stack Application Template with Authentication, RBAC, and Admin Panel.

## Tech Stack

- **Backend**: Python 3.12 + FastAPI
- **Frontend**: Next.js 16 (React 19, TypeScript)
- **Database**: PostgreSQL 17
- **Cache/Queue**: Redis 8
- **ORM**: SQLAlchemy 2.0 + Alembic migrations
- **Task Queue**: Celery with Redis broker
- **Email Testing**: Mailpit (development)
- **Deployment**: Docker Compose

## Project Structure

```
BaseApp/
├── CLAUDE.md                 # This file
├── docker-compose.yml
├── README.md
│
├── API/                      # REST Client test files
│   ├── auth.rest             # Authentication endpoints
│   ├── admin-users.rest      # User management
│   ├── admin-rbac.rest       # Roles & permissions
│   └── admin-config.rest     # Configuration/settings
│
├── .env.example              # Environment template for nginx
│
├── backend/                  # FastAPI Backend
│   ├── .env                  # Environment variables
│   ├── .env.example          # Environment template
│   ├── app/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── database.py       # DB connection
│   │   ├── startup.py        # Auto-seed roles & permissions
│   │   │
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py       # User model
│   │   │   ├── rbac.py       # Role & Permission models
│   │   │   ├── config.py     # AppConfig model
│   │   │   └── password_reset.py
│   │   │
│   │   ├── api/              # API routes
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   └── admin/
│   │   │       ├── users.py  # User management
│   │   │       ├── rbac.py   # Roles & permissions
│   │   │       └── config.py # Configuration
│   │   │
│   │   ├── tasks/            # Celery background tasks
│   │   │   └── email.py      # Email tasks
│   │   │
│   │   └── utils/
│   │       └── permissions.py
│   │
│   ├── alembic/              # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                 # Next.js 16 Frontend
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── login/        # Login page
│   │   │   ├── signup/       # Signup page
│   │   │   ├── forgot-password/
│   │   │   ├── reset-password/
│   │   │   ├── dashboard/    # User dashboard
│   │   │   │   └── profile/  # User profile
│   │   │   ├── admin/        # Admin panel
│   │   │   │   ├── users/    # User management
│   │   │   │   ├── roles/    # Role management
│   │   │   │   ├── settings/ # App settings
│   │   │   │   └── profile/  # Admin profile
│   │   │   └── profile/      # Profile redirect
│   │   │
│   │   ├── components/
│   │   │   └── ProfileContent.tsx
│   │   │
│   │   └── lib/
│   │       └── api.ts        # API client
│   │
│   ├── package.json
│   └── Dockerfile
│
└── .vscode/
    └── settings.json         # REST Client config
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

### Implemented

- Database driven configuration
- User signup/login with JWT authentication
- Password reset via email (Mailpit for testing)
- Role-Based Access Control (RBAC)
- Permission-based access management
- Profile management (update details, change password)
- Admin panel with dark sidebar theme
- User management (view, edit, activate/deactivate)
- Role management (create, edit, delete, copy permissions)
- Settings management (admin)

### Planned

- Multi-language support
- Email notifications (production SMTP)
- 2FA authentication
- Password Generator
- Session & device Management

## Priority Order (MVP)

1. **Backend Setup** - FastAPI app, database, Docker
1. **Auth** - Signup, login, JWT middleware, Profile & password update
1. **Frontend Setup** - Next.js, Tailwind, shadcn/ui
1. **Auth UI** - Login, signup, reset password pages
1. **Admin** - Users views, Application Configuration
1. **Polish** - Error handling, loading states, store logs rotating log files

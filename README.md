# SampleApp

SampleApp is a Sample Application Template

## Quick Start

### Prerequisites

- Docker & Docker Compose

### 1. Clone and Configure

```bash
# Copy environment files
cp backend/.env.example backend/.env

# Edit backend/.env with your VHI credentials
```

### 2. Start Development Environment

```bash
docker compose up -d
```

This starts:

- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Backend API** on http://localhost:8000
- **Frontend** on http://localhost:3000

### 3. Run Database Migrations

```bash
docker compose exec backend alembic upgrade head
```

### 4. Seed Initial Data

```bash
docker compose exec backend python -m app.seed
```

This creates:

- Roles: Admin, User (Default)
- Admin user: `admin@domain.com` / `admin123`
- Basic Permission for Admin & User

### 5. Access the Application

- **Customer Dashboard**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin (login as admin first)
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
app/
├── CLAUDE.md              # Claude Code context
├── docker compose.yml     # Development containers
├── backend/               # FastAPI Backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models/       # SQLAlchemy models
│   │   └── tasks/        # Celery tasks
│   ├── alembic/          # Database migrations
│   └── requirements.txt
└── frontend/              # Next.js 16 Frontend
    ├── src/
    │   ├── app/          # App Router pages
    │   ├── components/   # React components
    │   └── lib/          # Utilities
    └── package.json
```

## Development Commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery

# Run backend shell
docker compose exec backend bash

# Run migrations
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Access database
docker compose exec db psql -U cloudpe -d cloudpe

# Rebuild containers
docker compose build --no-cache
```

## API Endpoints

### Authentication

- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login (returns JWT)
- `GET /api/auth/me` - Get current user

### Admin

- `GET /api/admin/users` - List all users
- `PATCH /api/admin/users/{id}` - Update user

## MVP Features

### ✅ Included

- User signup/login with JWT authentication
- Admin panel for users
- Multi-region support

### 🔜 Coming Later

- Email notifications
- 2FA authentication

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Celery
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Infrastructure**: Docker Compose

## License

MIT

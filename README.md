# SampleApp

A full-stack application template with authentication, RBAC, and admin panel.

## Features

### Authentication & Authorization

- User signup/login with JWT authentication
- Password reset via email
- Role-Based Access Control (RBAC)
- Permission-based access management

### User Management

- Profile management (update details, change password)
- Admin user management panel
- User activation/deactivation
- Role assignment

### Admin Panel

- Dashboard with dark sidebar theme
- User management (view, edit, activate/deactivate)
- Role management (create, edit, delete, copy permissions)
- Settings management

### Roles & Permissions

- **Super Admin**: Full system control (CLI only, hidden from UI)
- **Administrator**: User and role management
- **Standard User**: Basic access

## Quick Start

### Prerequisites

- Docker & Docker Compose

### 1. Clone and Configure

```bash
# Copy environment file
cp backend/.env.example backend/.env

# Edit backend/.env if needed (defaults work for development)
```

### 2. Start Development Environment

```bash
docker compose up -d
```

This starts:

| Service     | URL                   | Description      |
| ----------- | --------------------- | ---------------- |
| PostgreSQL  | localhost:5432        | Database         |
| Redis       | localhost:6379        | Cache & Queue    |
| Backend API | http://localhost:8000 | FastAPI Backend  |
| Frontend    | http://localhost:3000 | Next.js Frontend |
| Mailpit     | http://localhost:8025 | Email Testing UI |

### 3. Access the Application

- **Login**: http://localhost:3000/login
- **API Docs**: http://localhost:8000/docs
- **Email Inbox**: http://localhost:8025

**Default Super Admin:**

- Email: `admin@example.com`
- Password: `Admin@123`
  (If not configured in .env)
  > Note: Migrations and seed data run automatically on startup.

## Email Testing with Mailpit

All emails sent by the application are captured by Mailpit in development.

- **Web UI**: http://localhost:8025
- **SMTP**: localhost:1025

Test the password reset flow:

1. Go to http://localhost:3000/forgot-password
2. Enter an email address
3. Check Mailpit at http://localhost:8025 for the reset email

## Project Structure

```
BaseApp/
├── CLAUDE.md              # Claude Code context
├── docker-compose.yml     # Development containers
├── README.md
│
├── docs/                  # Referance documentations
│   └──API/                # REST Client test files
│
├── backend/               # FastAPI Backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   │   ├── auth.py   # Authentication endpoints
│   │   │   └── admin/    # Admin API routes
│   │   ├── models/       # SQLAlchemy models
│   │   │   ├── user.py   # User model
│   │   │   └── rbac.py   # Role & Permission models
│   │   ├── tasks/        # Celery background tasks
│   │   └── startup.py    # Auto-seed roles & permissions
│   ├── alembic/          # Database migrations
│   └── requirements.txt
│
└── frontend/              # Next.js 16 Frontend
    ├── src/
    │   ├── app/          # App Router pages
    │   │   ├── login/    # Login page
    │   │   ├── signup/   # Signup page
    │   │   ├── dashboard/# User dashboard
    │   │   ├── admin/    # Admin panel
    │   │   └── profile/  # Profile redirect
    │   ├── components/   # React components
    │   └── lib/          # Utilities
    └── package.json
```

## API Endpoints

For quick API testing in VSCode, use the [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client).

Pre-configured request files are available in the [`API/`](API/) folder:

### Authentication ([`API/auth.rest`](API/auth.rest))

| Method | Endpoint           | Description               |
| ------ | ------------------ | ------------------------- |
| POST   | `/signup`          | Register new user         |
| POST   | `/login`           | Login (returns JWT)       |
| GET    | `/me`              | Get current user          |
| PATCH  | `/profile`         | Update profile            |
| POST   | `/change-password` | Change password           |
| POST   | `/forgot-password` | Request password reset    |
| POST   | `/reset-password`  | Reset password with token |

### Admin Users ([`API/admin-users.rest`](API/admin-users.rest))

| Method | Endpoint | Description      |
| ------ | -------- | ---------------- |
| GET    | `/`      | List all users   |
| GET    | `/{id}`  | Get user details |
| PATCH  | `/{id}`  | Update user      |

### Roles & permissions (admin) ([`API/admin-rbac.rest`](API/admin-rbac.rest))

| Method | Endpoint                      | Description                              |
| ------ | ----------------------------- | ---------------------------------------- |
| GET    | `/roles`                      | List roles                               |
| POST   | `/roles`                      | Create role (supports copy_from_role_id) |
| PATCH  | `/roles/{id}`                 | Update role                              |
| DELETE | `/roles/{id}`                 | Delete role                              |
| GET    | `/permissions`                | List permissions                         |
| PUT    | `/roles/{id}/permissions`     | Set role permissions                     |
| POST   | `/users/{id}/roles/{role_id}` | Assign role to user                      |
| DELETE | `/users/{id}/roles/{role_id}` | Remove role from user                    |

### Configuration/settings (admin) ([`API/admin-config.rest`](API/admin-config.rest))

| Method | Endpoint       | Description                    |
| ------ | -------------- | ------------------------------ |
| GET    | `/`            | List all config items          |
| GET    | `/categories`  | List all categories            |
| GET    | `/by-category` | Get config grouped by category |
| GET    | `/{key}`       | Get single config item         |
| PUT    | `/{key}`       | Update single config item      |
| PUT    | `/`            | Bulk update config items       |
| POST   | `/clear-cache` | Clear cache and seed defaults  |

**Quick Start:**

1. Install the REST Client extension in VSCode
2. Open any `.rest` file from `API/` folder
3. Run the login request first to get a JWT token
4. Copy the token and update the `@token` variable
5. Click "Send Request" above any request to execute it

## Development Commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery

# Restart services
docker compose restart backend
docker compose restart frontend

# Run backend shell
docker compose exec backend bash

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Access database
docker compose exec db psql -U cloudpe -d cloudpe

# Create additional super admin
docker compose exec -it backend python -m app.create_admin

# Rebuild containers
docker compose build --no-cache
docker compose up -d
```

## Environment Variables

Key environment variables (see `backend/.env.example` for full list):

| Variable              | Description            | Default                   |
| --------------------- | ---------------------- | ------------------------- |
| `SECRET_KEY`          | JWT signing key        | (generate for production) |
| `SUPERADMIN_EMAIL`    | Initial admin email    | admin@example.com         |
| `SUPERADMIN_PASSWORD` | Initial admin password | Admin@123                 |
| `SMTP_HOST`           | Email server           | mailpit                   |
| `SMTP_PORT`           | Email port             | 1025                      |

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Celery
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 17
- **Cache/Queue**: Redis 8
- **Email Testing**: Mailpit
- **Infrastructure**: Docker Compose

## Production Deployment

For production:

1. Generate a secure `SECRET_KEY`:

   ```bash
   openssl rand -hex 32
   ```

2. Configure real SMTP settings in `.env`

3. Set `ENVIRONMENT=production` and `DEBUG=false`

4. Use proper database credentials

5. Configure CORS origins for your domain

## License

MIT

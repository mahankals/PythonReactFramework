# Docker Compose - Service Matrix

## Current Architecture

API-Gateway-based Microservices Architecture with Database-per-Service pattern.

## Active Services

| Service | Container | Image/Build | Ports | Dependencies | Healthcheck |
|---------|-----------|-------------|-------|--------------|-------------|
| nginx | baseapp-nginx | nginx:alpine | `${NGINX_PORT:-80}:80` | backend, frontend | wget localhost/health |
| base-app-backend | baseapp-backend | ./backend | `${BASE_HTTP_PORT:-8000}:8000` | db, redis (healthy) | N/A |
| base-app-frontend | baseapp-frontend | ./frontend | `${FRONTEND_PORT:-3000}:3000` | backend | N/A |
| base-app-db | baseapp-db | postgres:17-alpine | `${BASE_DB_PORT:-5432}:5432` | - | pg_isready |
| redis | baseapp-redis | redis:8-alpine | `${REDIS_PORT:-6379}:6379` | - | redis-cli ping |
| mailpit | baseapp-mailpit | axllent/mailpit | `8025:8025`, `1025:1025` | - | N/A |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| NGINX_PORT | 80 | API Gateway port |
| BASE_HTTP_PORT | 8000 | Backend API port |
| FRONTEND_PORT | 3000 | Next.js dev server port |
| BASE_DB_PORT | 5432 | PostgreSQL port |
| REDIS_PORT | 6379 | Redis port |
| MAILPIT_HTTP_PORT | 8025 | Mailpit Web UI port |
| MAILPIT_SMTP_PORT | 1025 | Mailpit SMTP port |

## Volumes

| Volume | Mount Point | Service |
|--------|-------------|---------|
| base-app-db-data | /var/lib/postgresql/data | base-app-db |
| redis-data | /data | redis |

## Network

All services connected via `app-network` (bridge driver).

## Routing (nginx)

| Path | Upstream | Description |
|------|----------|-------------|
| `/api/*` | base-app-backend:8000 | Backend API endpoints |
| `/health` | nginx | Gateway health check |
| `/*` | base-app-frontend:3000 | Next.js frontend (catch-all) |

## Future Microservices (Template)

When adding new microservices, follow the database-per-service pattern:

```yaml
new-service:
  build: ./services/new-service
  container_name: new-service
  environment:
    DATABASE_URL: postgresql://user:pass@new-service-db:5432/dbname
  depends_on:
    new-service-db:
      condition: service_healthy
  networks:
    - app-network

new-service-db:
  image: postgres:17-alpine
  container_name: new-service-db
  environment:
    POSTGRES_USER: user
    POSTGRES_PASSWORD: pass
    POSTGRES_DB: dbname
  volumes:
    - new-service-db-data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U user -d dbname"]
    interval: 5s
    timeout: 5s
    retries: 5
  networks:
    - app-network
```

Then add nginx route:
```nginx
location /new-service/ {
    proxy_pass http://new-service:PORT/;
}
```

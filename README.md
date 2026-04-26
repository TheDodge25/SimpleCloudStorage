# Google Drive Clone

A self-hosted file manager built with **SvelteKit**, **FastAPI**, **MongoDB**, and **MinIO**, orchestrated with Docker Compose.

## Stack

| Layer | Technology |
|---|---|
| Frontend | SvelteKit + TailwindCSS v4 |
| Backend | FastAPI (Python 3.12) |
| Database | MongoDB 8 |
| Storage | MinIO (S3-compatible) |
| Proxy | nginx |
| CI | GitHub Actions |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 24+
- [Git](https://git-scm.com/)

---

## Quick Start (Docker — recommended)

```bash
# 1. Clone the repo
git clone <repo-url> && cd fullstack-test

# 2. Create your .env file
cp .env.example .env

# 3. Build and start all services
docker compose up --build

# 4. Open in browser
open http://localhost
```

The app will be available at **http://localhost** (port 80).

### Service URLs (while running)

| Service | URL |
|---|---|
| App | http://localhost |
| API docs (Swagger) | http://localhost:8000/docs |
| MinIO console | http://localhost:9001 (admin / minioadmin) |

---

## Local Development (without Docker)

Run MongoDB and MinIO in Docker, everything else natively.

```bash
# Start only the infrastructure containers
docker compose up -d mongo minio

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173  (Vite proxy forwards /api/* to :8000)
```

---

## Running Tests

The integration tests run against a live backend. Start the backend first.

```bash
# Ensure backend is running (see Local Development above)

cd backend
pip install -r requirements.txt
pytest tests/ -v
```

To run against a Docker deployment:

```bash
BACKEND_TEST_URL=http://localhost:8000 pytest tests/ -v
```

---

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|---|---|---|
| `MINIO_ROOT_USER` | `minioadmin` | MinIO admin username |
| `MINIO_ROOT_PASSWORD` | `minioadmin` | MinIO admin password |
| `MINIO_BUCKET_NAME` | `drive-files` | Bucket for uploaded files |
| `MINIO_ENDPOINT` | `minio:9000` | MinIO host (internal Docker) |
| `MONGO_URL` | `mongodb://mongo:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | `drivedb` | Database name |
| `BACKEND_URL` | `http://backend:8000` | FastAPI host (used by SvelteKit SSR) |
| `BACKEND_CORS_ORIGINS` | `http://localhost,...` | Allowed CORS origins |

---

## Project Structure

```
fullstack-test/
├── backend/              FastAPI application
│   ├── app/
│   │   ├── config.py     Pydantic settings
│   │   ├── database.py   Motor (MongoDB) client
│   │   ├── storage.py    MinIO client
│   │   ├── models/       Pydantic models
│   │   └── routes/       API route handlers
│   ├── tests/            pytest integration tests
│   └── Dockerfile
├── frontend/             SvelteKit application
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.js          Browser-side API client
│   │   │   ├── server/api.js   Server-side API client (SSR)
│   │   │   ├── stores.js       Svelte stores
│   │   │   └── components/     UI components
│   │   └── routes/             SvelteKit pages
│   └── Dockerfile
├── nginx/                Reverse proxy
│   ├── nginx.conf
│   └── Dockerfile
├── .env.example
└── docker-compose.yml
```

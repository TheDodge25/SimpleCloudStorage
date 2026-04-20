# Google Drive Clone

A self-hosted, single-user Google Drive clone built with:

- **Frontend**: SvelteKit + TailwindCSS v4
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (file metadata)
- **Object Storage**: MinIO (file blobs)
- **Orchestration**: Docker Compose

Dark-mode UI inspired by Google Drive. Supports nested folder hierarchy, file upload/download, filename search, and permanent delete.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Docker Desktop | Latest | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| Git | ≥ 2.39 | [git-scm.com](https://git-scm.com/) |
| Node.js | ≥ 20 | [nodejs.org](https://nodejs.org/) *(frontend dev only)* |
| Python | ≥ 3.11 | [python.org](https://www.python.org/) *(backend dev only)* |

> **Docker Desktop** is required to run the full stack. Download and install it before running `docker compose up`.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/TheDodge25/gdrive-clone.git
cd gdrive-clone

# 2. Copy env file (do not commit .env)
cp .env.example .env

# 3. Start all services
docker compose up --build

# 4. Open the app
#    Frontend  → http://localhost:3000
#    API docs  → http://localhost:8000/docs
#    MinIO UI  → http://localhost:9001  (user: minioadmin / minioadmin)
```

---

## Architecture

```
Browser
  │
  ▼
SvelteKit (port 3000)
  │  REST API (fetch)
  ▼
FastAPI (port 8000)
  │              │
  ▼              ▼
MongoDB        MinIO
(port 27017)   (port 9000 API / 9001 Console)

All services orchestrated by Docker Compose.
```

---

## Project Structure

```
fullstack-test/
├── frontend/          # SvelteKit app
├── backend/           # FastAPI app
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

> You'll still need MongoDB and MinIO running (via Docker or locally) for the backend to function.

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, tagged releases |
| `develop` | Active development |
| `feat/*` | Feature branches → merge to develop |
| `fix/*` | Bug fix branches → merge to develop |

---

## License

MIT

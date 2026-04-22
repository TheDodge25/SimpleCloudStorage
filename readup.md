# Reading List — Google Drive Clone

A curated guide to every technology used in this project.
Ordered by when you'll encounter them, with direct links to the most relevant docs sections.

---

## Phase 1 — Infrastructure

### 🐳 Docker & Docker Compose
**What it does here:** Runs MongoDB, MinIO, the backend, and the frontend as isolated containers. They talk to each other over an internal network using service names as hostnames (e.g. `mongo:27017`).

| Topic | URL |
|---|---|
| What is a container | https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/ |
| Dockerfile reference | https://docs.docker.com/reference/dockerfile/ |
| Docker Compose file reference | https://docs.docker.com/reference/compose-file/ |
| Networking in Compose | https://docs.docker.com/compose/how-tos/networking/ |
| Named volumes (persistence) | https://docs.docker.com/compose/how-tos/use-volumes/ |
| Health checks | https://docs.docker.com/reference/dockerfile/#healthcheck |
| Multi-stage builds | https://docs.docker.com/build/building/multi-stage/ |

> **Focus on:** service names as hostnames, `depends_on` with `condition: service_healthy`, and named volumes. These are the three things most likely to trip you up.

---

### 🔁 GitHub Actions (CI)
**What it does here:** Automatically runs lint, type checks, and a Docker build on every push/PR so broken code never silently merges.

| Topic | URL |
|---|---|
| Quickstart | https://docs.github.com/en/actions/writing-workflows/quickstart |
| Workflow syntax | https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions |
| `actions/checkout` | https://github.com/actions/checkout |
| `actions/setup-node` | https://github.com/actions/setup-node |
| `actions/setup-python` | https://github.com/actions/setup-python |

---

## Phase 2 — Backend

### ⚡ FastAPI
**What it does here:** The entire REST API layer. Handles routing, request validation, file uploads, streaming downloads, and auto-generates the Swagger UI at `/docs`.

| Topic | URL |
|---|---|
| First steps / overview | https://fastapi.tiangolo.com/tutorial/first-steps/ |
| Path parameters | https://fastapi.tiangolo.com/tutorial/path-params/ |
| Query parameters | https://fastapi.tiangolo.com/tutorial/query-params/ |
| Request body (JSON) | https://fastapi.tiangolo.com/tutorial/body/ |
| File uploads (`UploadFile`) | https://fastapi.tiangolo.com/tutorial/request-files/ |
| Error handling (`HTTPException`) | https://fastapi.tiangolo.com/tutorial/handling-errors/ |
| CORS middleware | https://fastapi.tiangolo.com/tutorial/middleware/ |
| `StreamingResponse` for downloads | https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse |
| Dependency injection | https://fastapi.tiangolo.com/tutorial/dependencies/ |
| `APIRouter` (splitting routes) | https://fastapi.tiangolo.com/tutorial/bigger-applications/ |
| Lifespan events (startup/shutdown) | https://fastapi.tiangolo.com/advanced/events/ |

> **Must-read:** `UploadFile`, `StreamingResponse`, and lifespan events. These are the non-obvious patterns that power the upload/download core.

---

### 📦 Pydantic v2
**What it does here:** Validates all incoming request bodies and defines the shape of all API responses. FastAPI uses it automatically — you define a class, FastAPI enforces it.

| Topic | URL |
|---|---|
| Models basics | https://docs.pydantic.dev/latest/concepts/models/ |
| Field validation & constraints | https://docs.pydantic.dev/latest/concepts/fields/ |
| Model config (aliases, etc.) | https://docs.pydantic.dev/latest/concepts/config/ |
| JSON serialization | https://docs.pydantic.dev/latest/concepts/serialization/ |

---

### ⚙️ pydantic-settings
**What it does here:** Reads environment variables from `.env` and maps them into a typed `Settings` class. Used in `config.py`.

| Topic | URL |
|---|---|
| Getting started | https://docs.pydantic.dev/latest/concepts/pydantic_settings/ |

---

### 🔄 Python `async` / `await`
**What it does here:** FastAPI is async-first. Every route function, every DB call, every file operation uses `async def` and `await` so the server can handle multiple requests concurrently without blocking.

| Topic | URL |
|---|---|
| Coroutines & tasks | https://docs.python.org/3/library/asyncio-task.html |
| FastAPI's concurrency explainer | https://fastapi.tiangolo.com/async/ |

---

### 🍃 MongoDB — Document Model
**What it does here:** Stores all file and folder metadata. Each file is a JSON-like document in the `files` collection; each folder is a document in the `folders` collection.

| Topic | URL |
|---|---|
| What is a document | https://www.mongodb.com/docs/manual/core/document/ |
| CRUD operations | https://www.mongodb.com/docs/manual/crud/ |
| Indexes | https://www.mongodb.com/docs/manual/indexes/ |
| ObjectId | https://www.mongodb.com/docs/manual/reference/method/ObjectId/ |

---

### 🔌 Motor — Async MongoDB Driver
**What it does here:** The Python library that lets FastAPI talk to MongoDB asynchronously. It's the async version of PyMongo — same API, just add `await`.

| Topic | URL |
|---|---|
| Tutorial (asyncio) | https://motor.readthedocs.io/en/stable/tutorial-asyncio.html |
| Collection API reference | https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html |

---

### 🔑 BSON / ObjectId
**What it does here:** MongoDB uses `ObjectId` (not plain strings) as document IDs. The `bson` library converts between string IDs (what the API receives) and `ObjectId` (what MongoDB stores).

| Topic | URL |
|---|---|
| ObjectId explained | https://www.mongodb.com/docs/manual/reference/bson-types/#objectid |
| bson Python package | https://pymongo.readthedocs.io/en/stable/api/bson/objectid.html |

---

### 🪣 MinIO Python SDK
**What it does here:** Stores the actual file contents as objects in a bucket. Three operations cover everything: `put_object` (upload), `get_object` (download/stream), `remove_object` (delete).

| Topic | URL |
|---|---|
| Python SDK quickstart | https://min.io/docs/minio/linux/developers/python/minio-py.html |
| `put_object` | https://min.io/docs/minio/linux/developers/python/API.html#put_object |
| `get_object` | https://min.io/docs/minio/linux/developers/python/API.html#get_object |
| `remove_object` | https://min.io/docs/minio/linux/developers/python/API.html#remove_object |

> **Key concept:** MinIO stores files as objects in a bucket (like a flat folder). The object name is the full "path" key — we use `uploads/<uuid>-<filename>` as the key to guarantee uniqueness.

---

### 🆔 Python `uuid`
**What it does here:** Generates a unique ID prefixed to every file's MinIO object key so two files with the same name never collide in storage, even after auto-rename.

| Topic | URL |
|---|---|
| `uuid.uuid4()` | https://docs.python.org/3/library/uuid.html |

---

### 🕐 Python `datetime` / `timezone`
**What it does here:** All timestamps stored in MongoDB are timezone-aware UTC datetimes, created with `datetime.now(timezone.utc)`.

| Topic | URL |
|---|---|
| `datetime` module | https://docs.python.org/3/library/datetime.html |
| Working with timezones | https://docs.python.org/3/library/datetime.html#timezone-objects |

---

## Phase 3 — Frontend (Upcoming)

### 🟠 SvelteKit
**What it does here:** The full frontend framework. Handles routing (file-based), server-side data loading, and reactive UI components.

| Topic | URL |
|---|---|
| Introduction | https://svelte.dev/docs/kit/introduction |
| Routing | https://svelte.dev/docs/kit/routing |
| `load` functions | https://svelte.dev/docs/kit/load |
| Form actions | https://svelte.dev/docs/kit/form-actions |
| Svelte component syntax | https://svelte.dev/docs/svelte/overview |
| Reactivity runes (`$state`, `$derived`) | https://svelte.dev/docs/svelte/$state |

---

### 🎨 TailwindCSS v4
**What it does here:** Utility-first CSS framework for styling. Compose styles directly in HTML using class names.

| Topic | URL |
|---|---|
| Installation with SvelteKit | https://tailwindcss.com/docs/installation/framework-guides/sveltekit |
| Core concepts | https://tailwindcss.com/docs/styling-with-utility-classes |
| Responsive design | https://tailwindcss.com/docs/responsive-design |
| Dark mode | https://tailwindcss.com/docs/dark-mode |
| Hover, focus & transitions | https://tailwindcss.com/docs/hover-focus-and-other-states |

---

## Recommended Reading Order

```
1. Docker basics + Compose networking     → understand how services connect
2. FastAPI tutorial (path/query/body)     → understand the API structure
3. Pydantic models                        → understand request/response shapes
4. MongoDB document model + CRUD          → understand what's stored and how
5. Motor async driver                     → understand how Python talks to MongoDB
6. MinIO SDK (put/get/remove)             → understand how files are stored
7. Python async/await                     → understand why everything is async
8. SvelteKit routing + load()             → understand the frontend shell
9. TailwindCSS core concepts              → understand styling approach
```

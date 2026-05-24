from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_indexes, close_connection
from app.storage import ensure_bucket
from app.routes import files, folders, search, auth, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_bucket()
    await create_indexes()
    yield
    await close_connection()


app = FastAPI(title="Drive Clone API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,  # Required for HttpOnly cookie auth
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(files.router)
app.include_router(folders.router)
app.include_router(search.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

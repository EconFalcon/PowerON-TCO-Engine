from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import CORS_ORIGINS
from app.database import init_db
from app.routers import calculate, vehicles, chargers, scenarios, export, reference

app = FastAPI(title="PowerOn TCO Calculator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(calculate.router)
app.include_router(vehicles.router)
app.include_router(chargers.router)
app.include_router(scenarios.router)
app.include_router(export.router)
app.include_router(reference.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

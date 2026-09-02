import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.db.database import db_manager
from app.db.schema import init_db
from app.api.v1.router import api_v1_router
from scripts.seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager handling database initialization and seed data population on startup."""
    with db_manager.get_connection() as conn:
        init_db(conn)

    # Automatically populate seed data if running in standalone/dev mode
    try:
        seed_database(db_manager)
    except Exception as e:
        print(f"Startup seed notice: {e}")

    yield


app = FastAPI(
    title="Volcanic Image/Data Observatory (VIDO) API",
    description=(
        "REST API service for the Volcanic Image/Data Observatory (VIDO). "
        "Provides multi-body terrestrial and planetary volcanology data access, "
        "composite metadata facet validation, coordinate conventions, spatial fallbacks, "
        "and chronological timeline aggregation."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_v1_router)

# Mount static files & media directories
static_dir = os.path.join(os.getcwd(), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

media_dir = os.path.join(os.getcwd(), "media")
if os.path.exists(media_dir):
    app.mount("/media", StaticFiles(directory=media_dir), name="media")


@app.get("/health", tags=["Health"], summary="API Health Check")
def health_check():
    """Returns the operational status of the VIDO API service."""
    return {"status": "healthy", "service": "VIDO API", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
def serve_index():
    """Serves the main VIDO scientific observatory frontend HTML view."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "VIDO API is running. Index file not found."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

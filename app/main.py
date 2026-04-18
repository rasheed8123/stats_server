from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from routes import admin, api

# Initialize FastAPI app
app = FastAPI(title="Cricket Heroes - Player Dashboard")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(api.router, prefix="/api", tags=["api"])


@app.get("/dashboard/bbl4", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard page"""
    with open(os.path.join(os.path.dirname(__file__), "templates/dashboard.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Cricket Heroes API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

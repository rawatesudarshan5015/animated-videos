"""
FastAPI application for Kids Video Enhancer Tool.
Main entry point for the backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, upload

app = FastAPI(title="Kids Video Enhancer API", version="0.1.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(upload.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Kids Video Enhancer API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

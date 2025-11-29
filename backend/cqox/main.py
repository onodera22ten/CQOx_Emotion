"""
FastAPI Main Application for Emotion CQOx
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import emotion

app = FastAPI(
    title="Emotion CQOx API",
    description="Emotional Episode Optimizer - Causal Decision Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(emotion.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Emotion CQOx API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import auth, logs, dashboard, insights, leaderboard, profile, ai

app = FastAPI(title=settings.PROJECT_NAME)

# CORS middleware - Updated for frontend connections
origins = [
    "http://localhost:8080",
    "http://localhost:8081", 
    "http://localhost:8082",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:8082",
    "https://eco-pulse-frontend.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoPulse API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
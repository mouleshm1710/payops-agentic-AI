from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health_router, agent_router, analytics_router

app = FastAPI(title="Agentic AI Payroll Operations Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router)
app.include_router(agent_router.router)
app.include_router(analytics_router.router)


@app.get("/")
def home():
    return {"message": "Backend is running successfully"}
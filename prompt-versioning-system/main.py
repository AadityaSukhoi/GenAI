"""
Entry point for the FastAPI application.
"""

from fastapi import FastAPI
from api.routes import prompt, evaluation
from db.database import Base, engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prompt Versioning System")

# Include routers
app.include_router(prompt.router, prefix="/prompts", tags=["Prompts"])
app.include_router(evaluation.router, prefix="/evaluate", tags=["Evaluation"])
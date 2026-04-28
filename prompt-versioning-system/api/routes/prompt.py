"""
API routes for prompt operations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import schemas
from services import prompt_service

router = APIRouter()


@router.post("/", response_model=schemas.PromptResponse)
def create_prompt(prompt: schemas.PromptCreate, db: Session = Depends(get_db)):
    return prompt_service.create_prompt(
        db, prompt.name, prompt.content, prompt.meta   
    )


@router.post("/{prompt_id}/version", response_model=schemas.PromptVersionResponse)
def create_version(prompt_id: int, data: schemas.PromptUpdate, db: Session = Depends(get_db)):
    return prompt_service.create_new_version(
        db, prompt_id, data.content, data.meta
    )


@router.get("/{prompt_id}/versions", response_model=list[schemas.PromptVersionResponse])
def get_versions(prompt_id: int, db: Session = Depends(get_db)):
    return prompt_service.get_versions(db, prompt_id)


@router.post("/{prompt_id}/rollback/{version}", response_model=schemas.PromptVersionResponse)
def rollback(prompt_id: int, version: int, db: Session = Depends(get_db)):
    return prompt_service.rollback(db, prompt_id, version)
"""
Service layer for prompt versioning and rollback logic.
"""

from sqlalchemy.orm import Session
from db import models


def create_prompt(db: Session, name: str, content: str, metadata: dict):
    """
    Create a new prompt with version 1.
    """
    prompt = models.Prompt(name=name)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    version = models.PromptVersion(
        prompt_id=prompt.id,
        version=1,
        content=content,
        metadata=metadata
    )
    db.add(version)
    db.commit()

    return prompt


def create_new_version(db: Session, prompt_id: int, content: str, metadata: dict):
    """
    Create a new version of an existing prompt.
    """
    last_version = (
        db.query(models.PromptVersion)
        .filter(models.PromptVersion.prompt_id == prompt_id)
        .order_by(models.PromptVersion.version.desc())
        .first()
    )

    new_version_number = last_version.version + 1

    # deactivate previous versions
    db.query(models.PromptVersion).filter(
        models.PromptVersion.prompt_id == prompt_id
    ).update({"is_active": False})

    new_version = models.PromptVersion(
        prompt_id=prompt_id,
        version=new_version_number,
        content=content,
        metadata=metadata,
        is_active=True
    )

    db.add(new_version)
    db.commit()

    return new_version


from fastapi import HTTPException


def rollback(db: Session, prompt_id: int, target_version: int):
    """
    Rollback to a specific version.
    """

    version = db.query(models.PromptVersion).filter(
        models.PromptVersion.prompt_id == prompt_id,
        models.PromptVersion.version == target_version
    ).first()

    if not version:
        raise HTTPException(
            status_code=404,
            detail=f"Version {target_version} not found for prompt {prompt_id}"
        )

    db.query(models.PromptVersion).filter(
        models.PromptVersion.prompt_id == prompt_id
    ).update({"is_active": False})

    version.is_active = True
    db.commit()

    return version


def get_versions(db: Session, prompt_id: int):
    """
    Retrieve all versions of a prompt.
    """
    return db.query(models.PromptVersion).filter(
        models.PromptVersion.prompt_id == prompt_id
    ).all()
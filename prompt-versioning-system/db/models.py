"""
Database models.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class Prompt(Base):
    """
    Represents a prompt entity.
    """
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    versions = relationship("PromptVersion", back_populates="prompt")


class PromptVersion(Base):
    """
    Represents a version of a prompt.
    """
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"))
    version = Column(Integer)
    content = Column(String)
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    prompt = relationship("Prompt", back_populates="versions")
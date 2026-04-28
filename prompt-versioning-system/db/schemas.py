"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional, Dict


class PromptCreate(BaseModel):
    name: str
    content: str
    meta: Optional[Dict] = {}


class PromptUpdate(BaseModel):
    content: str
    meta: Optional[Dict] = {}


class PromptResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PromptVersionResponse(BaseModel):
    version: int
    content: str
    meta: Optional[Dict]
    is_active: bool

    class Config:
        from_attributes = True
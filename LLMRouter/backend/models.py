from pydantic import BaseModel, Field
from typing import Optional, Literal

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's query text")
    model: Literal["gemini", "mistral", "granite", "auto"] = Field(
        default="auto", 
        description="The model to use for answering"
    )
    history: list[ChatMessage] = Field(default_factory=list, description="Array of past messages for context")

class ChatResponse(BaseModel):
    response: str
    model_used: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

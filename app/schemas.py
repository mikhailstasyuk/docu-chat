# app/schemas.py

from pydantic import BaseModel, Field
from typing import List

class IngestResponse(BaseModel):
    """Response model for a successful document ingestion."""
    message: str
    document_id: str
    chunks_stored: int

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    session_id: str = Field(..., description="A unique identifier for the conversation.", example="session-123")
    question: str = Field(..., example="What is the main topic of the document?")

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    session_id: str
    answer: str
    retrieved_context: bool = Field(..., description="Indicates if relevant context was found in the document.")

class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str
    
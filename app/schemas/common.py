from pydantic import BaseModel, Field
from typing import List, Optional


class ErrorResponse(BaseModel):
    """Standard API error response payload."""
    detail: str = Field(..., description="Human-readable error explanation")
    errors: Optional[List[str]] = Field(default=None, description="Optional granular validation error messages")

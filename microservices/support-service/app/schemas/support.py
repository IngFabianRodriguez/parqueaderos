"""Pydantic schemas for support-service."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Ticket schemas
class TicketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=50)
    priority: str = Field(default="medium", max_length=20)
    sede_id: Optional[str] = None


class TicketResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    created_by: str
    assigned_to: Optional[str] = None
    sede_id: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int


class TicketMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)
    is_internal: bool = False


class TicketMessageResponse(BaseModel):
    id: str
    ticket_id: str
    sender_id: str
    sender_type: str
    message: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Chat schemas
class ChatMessageSend(BaseModel):
    message: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    sender_id: str
    sender_type: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    agent_id: Optional[str] = None
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    rating: Optional[int] = None

    class Config:
        from_attributes = True


# SLA schemas
class SLAResponse(BaseModel):
    ticket_id: str
    priority: str
    response_time_minutes: int
    resolution_time_minutes: int
    sla_breached: bool


# Feedback / NPS schemas
class NPSSurveyCreate(BaseModel):
    score: int = Field(..., ge=0, le=10)
    feedback: Optional[str] = None
    ticket_id: Optional[str] = None


class NPSSurveyResponse(BaseModel):
    id: str
    tenant_id: str
    ticket_id: Optional[str] = None
    user_id: str
    score: int
    feedback: Optional[str] = None
    responded_at: datetime

    class Config:
        from_attributes = True


# Analytics
class SupportAnalyticsResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    avg_resolution_time_minutes: float
    nps_score: float
    tickets_by_category: dict
    tickets_by_priority: dict